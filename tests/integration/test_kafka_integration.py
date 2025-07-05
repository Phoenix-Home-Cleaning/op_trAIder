#!/usr/bin/env python3
"""
@fileoverview Comprehensive Kafka integration test suite for TRAIDER
@module tests.integration.test_kafka_integration

@description
Institutional-grade integration test coverage for Kafka/Redpanda messaging.
Tests include producer/consumer reliability, message processing, failure recovery,
high-throughput scenarios, and real-time trading data distribution.

@performance
- Message throughput: >50k messages/second
- End-to-end latency: <10ms
- Consumer lag: <100ms

@risk
- Failure impact: CRITICAL - Message loss affects trading decisions
- Recovery strategy: Dead letter queues and replay mechanisms

@compliance
- Audit requirements: Yes - All trading messages must be logged
- Message ordering: Strict ordering for trading signals

@see {@link docker-compose.yml} Redpanda configuration
@since 1.0.0-alpha.1
@author TRAIDER Team
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from unittest.mock import patch, AsyncMock

import pytest
try:
    from kafka import KafkaProducer, KafkaConsumer
    from kafka.errors import KafkaError
    from kafka.admin import KafkaAdminClient, NewTopic
except ModuleNotFoundError:
    import pytest as _pytest
    _pytest.skip("Skipping Kafka integration tests: kafka-python not available", allow_module_level=True)

# Import backend modules (when they exist)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

import importlib

# Skip entire module if kafka vendor six dependency is unavailable BEFORE attempting to import kafka
if importlib.util.find_spec("kafka.vendor.six.moves") is None:
    import pytest as _pytest
    _pytest.skip("Skipping Kafka integration tests: 'kafka.vendor.six' not available", allow_module_level=True)

class TestKafkaIntegration:
    """
    Kafka integration test suite for TRAIDER trading platform
    
    @description
    Comprehensive testing of Kafka/Redpanda messaging functionality including:
    - Producer reliability and performance
    - Consumer group management and failover
    - Message ordering and delivery guarantees
    - High-throughput trading data streaming
    - Dead letter queue handling
    - Partition management and scaling
    - Cross-service communication patterns
    - Failure recovery and resilience
    
    @tradingImpact Tests critical messaging infrastructure for real-time trading
    @riskLevel CRITICAL - Message failures affect entire trading system
    """

    # =============================================================================
    # TEST CONFIGURATION
    # =============================================================================

    KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
    TEST_TOPICS = [
        'market-data-test',
        'trading-signals-test', 
        'order-execution-test',
        'risk-events-test',
        'system-alerts-test'
    ]
    
    @pytest.fixture(scope="class")
    async def setup_kafka_infrastructure(self):
        """
        Setup Kafka topics and infrastructure for testing.
        
        @description
        Creates test topics, configures partitions and replication,
        and ensures Kafka cluster is ready for testing.
        
        @performance Target: <5s infrastructure setup
        @tradingImpact Kafka infrastructure essential for message tests
        @riskLevel HIGH - Test infrastructure setup
        """
        # Create admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            client_id="traider-test-admin"
        )
        
        # Create test topics
        topics = [
            NewTopic(
                name=topic,
                num_partitions=3,
                replication_factor=1,
                topic_configs={
                    'retention.ms': '86400000',  # 24 hours
                    'cleanup.policy': 'delete',
                    'compression.type': 'lz4',
                    'max.message.bytes': '1048576'  # 1MB
                }
            )
            for topic in self.TEST_TOPICS
        ]
        
        try:
            # Delete existing test topics
            admin_client.delete_topics(self.TEST_TOPICS, timeout=10)
            await asyncio.sleep(2)  # Wait for deletion
        except Exception:
            pass  # Topics might not exist
        
        # Create new topics
        admin_client.create_topics(topics, timeout=10)
        await asyncio.sleep(2)  # Wait for creation
        
        yield
        
        # Cleanup
        try:
            admin_client.delete_topics(self.TEST_TOPICS, timeout=10)
        except Exception:
            pass
        
        admin_client.close()

    @pytest.fixture
    def sample_market_data_messages(self) -> List[Dict[str, Any]]:
        """
        Create sample market data messages for testing.
        
        @description
        Generates realistic market data messages for testing
        high-throughput streaming and processing.
        
        @returns List of market data message dictionaries
        @tradingImpact Sample messages for testing market data workflows
        @riskLevel LOW - Test data generation
        """
        messages = []
        base_time = datetime.now(timezone.utc)
        
        for i in range(1000):
            timestamp = base_time + timedelta(milliseconds=i)
            price = 50000.00 + (i * 0.01)
            
            message = {
                'message_id': str(uuid.uuid4()),
                'timestamp': timestamp.isoformat(),
                'symbol': 'BTC-USD',
                'event_type': 'tick',
                'data': {
                    'price': price,
                    'volume': 1.5 + (i * 0.001),
                    'bid': price - 0.01,
                    'ask': price + 0.01,
                    'trade_count': 1,
                    'exchange': 'coinbase'
                },
                'metadata': {
                    'source': 'market-data-service',
                    'version': '1.0.0',
                    'sequence': i
                }
            }
            messages.append(message)
        
        return messages

    @pytest.fixture
    def sample_trading_signals(self) -> List[Dict[str, Any]]:
        """
        Create sample trading signal messages for testing.
        
        @description
        Generates realistic trading signal messages for testing
        signal distribution and processing workflows.
        
        @returns List of trading signal message dictionaries
        @tradingImpact Sample signals for testing signal workflows
        @riskLevel LOW - Test data generation
        """
        signals = []
        base_time = datetime.now(timezone.utc)
        
        for i in range(100):
            timestamp = base_time + timedelta(seconds=i)
            
            signal = {
                'signal_id': str(uuid.uuid4()),
                'timestamp': timestamp.isoformat(),
                'symbol': 'BTC-USD',
                'event_type': 'signal_generated',
                'data': {
                    'signal_type': 'buy' if i % 2 == 0 else 'sell',
                    'strength': 0.1 + (i % 10) * 0.1,
                    'confidence': 0.5 + (i % 5) * 0.1,
                    'target_price': 50000.00 + (i * 10),
                    'stop_loss': 49000.00 + (i * 10),
                    'position_size': 0.1,
                    'strategy': 'momentum_v1'
                },
                'metadata': {
                    'source': 'signal-generation-service',
                    'model_version': '1.2.3',
                    'backtest_sharpe': 1.8,
                    'sequence': i
                }
            }
            signals.append(signal)
        
        return signals

    # =============================================================================
    # PRODUCER TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_producer_reliability_and_performance(self, setup_kafka_infrastructure, sample_market_data_messages):
        """
        Test Kafka producer reliability and performance benchmarks.
        
        @description
        Tests producer message sending with delivery guarantees,
        performance benchmarks, and error handling scenarios.
        
        @performance Target: >50k messages/second throughput
        @tradingImpact Producer reliability critical for real-time data
        @riskLevel HIGH - Producer failures affect data distribution
        """
        # Create producer with institutional-grade configuration
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            client_id='traider-test-producer',
            acks='all',  # Wait for all replicas
            retries=3,
            batch_size=16384,
            linger_ms=1,  # Low latency
            buffer_memory=33554432,
            compression_type='lz4',
            max_in_flight_requests_per_connection=1,  # Preserve ordering
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        
        try:
            start_time = time.time()
            futures = []
            
            # Send messages with performance tracking
            for i, message in enumerate(sample_market_data_messages):
                key = f"BTC-USD-{i}"
                future = producer.send(
                    'market-data-test',
                    value=message,
                    key=key,
                    partition=i % 3  # Distribute across partitions
                )
                futures.append(future)
            
            # Wait for all messages to be sent
            producer.flush()
            send_time = time.time() - start_time
            
            # Verify all messages were sent successfully
            successful_sends = 0
            for future in futures:
                try:
                    record_metadata = future.get(timeout=10)
                    assert record_metadata.topic == 'market-data-test'
                    assert record_metadata.partition in [0, 1, 2]
                    successful_sends += 1
                except KafkaError as e:
                    pytest.fail(f"Message send failed: {e}")
            
            assert successful_sends == len(sample_market_data_messages)
            
            # Performance benchmark
            messages_per_second = len(sample_market_data_messages) / send_time
            assert messages_per_second > 50000, f"Producer throughput {messages_per_second:.0f} msg/sec, expected >50k"
            
        finally:
            producer.close()

    @pytest.mark.asyncio
    async def test_producer_error_handling_and_retry(self, setup_kafka_infrastructure):
        """
        Test producer error handling and retry mechanisms.
        
        @description
        Tests producer behavior under error conditions including
        network failures, broker unavailability, and retry logic.
        
        @performance Target: <5s error recovery time
        @tradingImpact Error handling critical for system resilience
        @riskLevel HIGH - Error handling affects message reliability
        """
        # Create producer with retry configuration
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            client_id='traider-test-producer-retry',
            acks='all',
            retries=5,
            retry_backoff_ms=100,
            request_timeout_ms=5000,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        try:
            # Test with valid message first
            test_message = {
                'test_id': str(uuid.uuid4()),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': 'error_handling_test'
            }
            
            future = producer.send('market-data-test', value=test_message)
            record_metadata = future.get(timeout=10)
            assert record_metadata.topic == 'market-data-test'
            
            # Test with oversized message (should fail)
            oversized_message = {
                'test_id': str(uuid.uuid4()),
                'data': 'x' * (2 * 1024 * 1024)  # 2MB message (exceeds 1MB limit)
            }
            
            with pytest.raises(KafkaError):
                future = producer.send('market-data-test', value=oversized_message)
                future.get(timeout=10)
            
        finally:
            producer.close()

    @pytest.mark.asyncio
    async def test_producer_partitioning_strategy(self, setup_kafka_infrastructure):
        """
        Test producer partitioning strategies for trading data.
        
        @description
        Tests message partitioning strategies to ensure optimal
        distribution and ordering for trading data streams.
        
        @performance Target: Even partition distribution
        @tradingImpact Partitioning affects message ordering and performance
        @riskLevel MEDIUM - Partitioning strategy affects scalability
        """
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            client_id='traider-test-producer-partition',
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8')
        )
        
        try:
            partition_counts = {0: 0, 1: 0, 2: 0}
            symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD']
            
            # Send messages with symbol-based partitioning
            for i in range(300):  # 100 messages per symbol
                symbol = symbols[i % 3]
                message = {
                    'symbol': symbol,
                    'sequence': i,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'price': 1000.0 + i
                }
                
                future = producer.send(
                    'market-data-test',
                    value=message,
                    key=symbol  # Partition by symbol
                )
                
                record_metadata = future.get(timeout=10)
                partition_counts[record_metadata.partition] += 1
            
            # Verify partition distribution
            total_messages = sum(partition_counts.values())
            assert total_messages == 300
            
            # Each partition should have messages (not necessarily equal due to key hashing)
            for partition, count in partition_counts.items():
                assert count > 0, f"Partition {partition} received no messages"
            
        finally:
            producer.close()

    # =============================================================================
    # CONSUMER TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_consumer_group_management(self, setup_kafka_infrastructure, sample_market_data_messages):
        """
        Test consumer group management and load balancing.
        
        @description
        Tests consumer group coordination, partition assignment,
        and load balancing across multiple consumers.
        
        @performance Target: <500ms consumer group rebalancing
        @tradingImpact Consumer reliability critical for message processing
        @riskLevel HIGH - Consumer failures affect message processing
        """
        # First, produce test messages
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        for message in sample_market_data_messages[:100]:  # Send 100 messages
            producer.send('market-data-test', value=message)
        producer.flush()
        producer.close()
        
        # Create multiple consumers in the same group
        consumers = []
        consumed_messages = []
        
        try:
            for i in range(2):  # 2 consumers in the group
                consumer = KafkaConsumer(
                    'market-data-test',
                    bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                    group_id='traider-test-consumer-group',
                    client_id=f'traider-test-consumer-{i}',
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    consumer_timeout_ms=5000
                )
                consumers.append(consumer)
            
            # Consume messages from both consumers
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                for i, consumer in enumerate(consumers):
                    messages = consumer.poll(timeout_ms=1000)
                    for topic_partition, records in messages.items():
                        for record in records:
                            consumed_messages.append({
                                'consumer_id': i,
                                'partition': record.partition,
                                'offset': record.offset,
                                'message': record.value
                            })
                
                if len(consumed_messages) >= 100:
                    break
            
            # Verify all messages were consumed
            assert len(consumed_messages) == 100, f"Expected 100 messages, got {len(consumed_messages)}"
            
            # Verify load balancing (both consumers should have processed messages)
            consumer_0_messages = [m for m in consumed_messages if m['consumer_id'] == 0]
            consumer_1_messages = [m for m in consumed_messages if m['consumer_id'] == 1]
            
            assert len(consumer_0_messages) > 0, "Consumer 0 processed no messages"
            assert len(consumer_1_messages) > 0, "Consumer 1 processed no messages"
            
        finally:
            for consumer in consumers:
                consumer.close()

    @pytest.mark.asyncio
    async def test_consumer_offset_management(self, setup_kafka_infrastructure):
        """
        Test consumer offset management and commit strategies.
        
        @description
        Tests offset management, manual commits, and recovery
        from different offset positions for reliable processing.
        
        @performance Target: <100ms offset commit time
        @tradingImpact Offset management critical for message reliability
        @riskLevel HIGH - Offset errors cause message loss or duplication
        """
        # Produce test messages
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        test_messages = [
            {'id': i, 'data': f'test_message_{i}'}
            for i in range(50)
        ]
        
        for message in test_messages:
            producer.send('market-data-test', value=message)
        producer.flush()
        producer.close()
        
        # Test manual offset management
        consumer = KafkaConsumer(
            'market-data-test',
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id='traider-test-offset-group',
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            consumed_count = 0
            commit_points = []
            
            # Consume and manually commit at intervals
            for message in consumer:
                consumed_count += 1
                
                # Commit every 10 messages
                if consumed_count % 10 == 0:
                    start_time = time.time()
                    consumer.commit()
                    commit_time = (time.time() - start_time) * 1000
                    commit_points.append(commit_time)
                    
                    # Performance check
                    assert commit_time < 100, f"Offset commit took {commit_time:.2f}ms, expected <100ms"
                
                if consumed_count >= 50:
                    break
            
            # Final commit
            consumer.commit()
            
            # Verify all messages were processed
            assert consumed_count == 50, f"Expected 50 messages, processed {consumed_count}"
            assert len(commit_points) >= 4, "Should have committed at least 4 times"
            
        finally:
            consumer.close()

    @pytest.mark.asyncio
    async def test_consumer_failure_recovery(self, setup_kafka_infrastructure):
        """
        Test consumer failure recovery and rebalancing.
        
        @description
        Tests consumer failure scenarios, automatic recovery,
        and partition rebalancing when consumers fail.
        
        @performance Target: <5s failure recovery time
        @tradingImpact Consumer recovery critical for system resilience
        @riskLevel HIGH - Consumer failures affect message processing
        """
        # Produce test messages
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        for i in range(100):
            message = {'id': i, 'timestamp': datetime.now(timezone.utc).isoformat()}
            producer.send('market-data-test', value=message)
        producer.flush()
        producer.close()
        
        # Create primary consumer
        primary_consumer = KafkaConsumer(
            'market-data-test',
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id='traider-test-recovery-group',
            auto_offset_reset='earliest',
            session_timeout_ms=6000,
            heartbeat_interval_ms=2000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        # Create backup consumer
        backup_consumer = KafkaConsumer(
            'market-data-test',
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id='traider-test-recovery-group',
            auto_offset_reset='earliest',
            session_timeout_ms=6000,
            heartbeat_interval_ms=2000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            # Primary consumer processes some messages
            primary_messages = 0
            start_time = time.time()
            
            for message in primary_consumer:
                primary_messages += 1
                if primary_messages >= 30:  # Process 30 messages then "fail"
                    break
            
            # Simulate primary consumer failure by closing it
            primary_consumer.close()
            
            # Backup consumer should take over
            backup_messages = 0
            recovery_start = time.time()
            
            # Give time for rebalancing
            await asyncio.sleep(2)
            
            for message in backup_consumer:
                backup_messages += 1
                if backup_messages >= 20:  # Process remaining messages
                    break
            
            recovery_time = time.time() - recovery_start
            
            # Verify recovery
            assert backup_messages > 0, "Backup consumer did not process any messages"
            assert recovery_time < 10, f"Recovery took {recovery_time:.2f}s, expected <10s"
            
        finally:
            try:
                primary_consumer.close()
            except:
                pass
            backup_consumer.close()

    # =============================================================================
    # MESSAGE ORDERING TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_message_ordering_guarantees(self, setup_kafka_infrastructure):
        """
        Test message ordering guarantees for trading signals.
        
        @description
        Tests strict message ordering within partitions for
        trading signals and critical trading data.
        
        @performance Target: Strict ordering preservation
        @tradingImpact Message ordering critical for trading logic
        @riskLevel CRITICAL - Out-of-order messages affect trading decisions
        """
        # Produce ordered messages to single partition
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8'),
            max_in_flight_requests_per_connection=1,  # Preserve ordering
            acks='all'
        )
        
        # Send 100 ordered messages to same partition (same key)
        sent_sequence = []
        for i in range(100):
            message = {
                'sequence': i,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'symbol': 'BTC-USD',
                'signal_type': 'buy' if i % 2 == 0 else 'sell'
            }
            
            producer.send(
                'trading-signals-test',
                value=message,
                key='BTC-USD'  # Same key = same partition
            )
            sent_sequence.append(i)
        
        producer.flush()
        producer.close()
        
        # Consume and verify ordering
        consumer = KafkaConsumer(
            'trading-signals-test',
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            group_id='traider-test-ordering-group',
            auto_offset_reset='earliest',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            received_sequence = []
            
            for message in consumer:
                received_sequence.append(message.value['sequence'])
                if len(received_sequence) >= 100:
                    break
            
            # Verify strict ordering
            assert len(received_sequence) == 100, f"Expected 100 messages, got {len(received_sequence)}"
            assert received_sequence == sent_sequence, "Message ordering was not preserved"
            
            # Verify no gaps in sequence
            for i, seq in enumerate(received_sequence):
                assert seq == i, f"Sequence gap detected: expected {i}, got {seq}"
                
        finally:
            consumer.close()

    # =============================================================================
    # HIGH-THROUGHPUT TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_high_throughput_streaming(self, setup_kafka_infrastructure):
        """
        Test high-throughput message streaming for market data.
        
        @description
        Tests system performance under high message volume
        typical of real-time market data streaming.
        
        @performance Target: >100k messages/second sustained throughput
        @tradingImpact High throughput critical for real-time market data
        @riskLevel HIGH - Throughput affects real-time trading capabilities
        """
        # High-performance producer configuration
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            client_id='traider-test-high-throughput',
            acks=1,  # Leader acknowledgment only for speed
            batch_size=65536,  # Large batches
            linger_ms=5,  # Small delay for batching
            compression_type='lz4',
            buffer_memory=67108864,  # 64MB buffer
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # Generate high-volume test data
        message_count = 10000
        start_time = time.time()
        
        try:
            # Send messages as fast as possible
            for i in range(message_count):
                message = {
                    'tick_id': i,
                    'symbol': 'BTC-USD',
                    'price': 50000.0 + (i * 0.01),
                    'volume': 1.0,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                producer.send('market-data-test', value=message)
                
                # Don't wait for individual sends - let batching work
                if i % 1000 == 0:
                    producer.flush()  # Periodic flush
            
            # Final flush and timing
            producer.flush()
            send_time = time.time() - start_time
            
            # Performance validation
            throughput = message_count / send_time
            assert throughput > 50000, f"Throughput {throughput:.0f} msg/sec, expected >50k"
            
            # Test consumer throughput
            consumer = KafkaConsumer(
                'market-data-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='traider-test-throughput-consumer',
                auto_offset_reset='earliest',
                fetch_min_bytes=1024,  # Batch fetching
                fetch_max_wait_ms=500,
                max_partition_fetch_bytes=1048576,  # 1MB
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            consume_start = time.time()
            consumed_count = 0
            
            for message in consumer:
                consumed_count += 1
                if consumed_count >= message_count:
                    break
            
            consume_time = time.time() - consume_start
            consumer_throughput = consumed_count / consume_time
            
            assert consumer_throughput > 30000, f"Consumer throughput {consumer_throughput:.0f} msg/sec, expected >30k"
            
            consumer.close()
            
        finally:
            producer.close()

    # =============================================================================
    # DEAD LETTER QUEUE TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_dead_letter_queue_handling(self, setup_kafka_infrastructure):
        """
        Test dead letter queue handling for failed messages.
        
        @description
        Tests dead letter queue functionality for messages that
        fail processing, ensuring no message loss in trading system.
        
        @performance Target: <1s DLQ message routing
        @tradingImpact DLQ handling prevents message loss
        @riskLevel HIGH - Message loss affects trading accuracy
        """
        # This test simulates DLQ functionality that would be implemented
        # in the actual message processing services
        
        # Create DLQ topic
        admin_client = KafkaAdminClient(bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS)
        dlq_topic = NewTopic(
            name='market-data-dlq-test',
            num_partitions=1,
            replication_factor=1
        )
        
        try:
            admin_client.create_topics([dlq_topic], timeout=10)
            await asyncio.sleep(1)
        except Exception:
            pass  # Topic might already exist
        
        # Producer for main topic
        producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # DLQ producer
        dlq_producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        try:
            # Send test messages (some valid, some invalid)
            test_messages = [
                {'id': 1, 'valid': True, 'price': 50000.0},
                {'id': 2, 'valid': False, 'price': 'invalid'},  # Invalid price
                {'id': 3, 'valid': True, 'price': 50001.0},
                {'id': 4, 'valid': False, 'data': None},  # Missing required field
                {'id': 5, 'valid': True, 'price': 50002.0}
            ]
            
            for message in test_messages:
                producer.send('market-data-test', value=message)
            producer.flush()
            
            # Simulate message processing with DLQ routing
            consumer = KafkaConsumer(
                'market-data-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='traider-test-dlq-processor',
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            processed_count = 0
            dlq_count = 0
            
            for message in consumer:
                try:
                    # Simulate message processing
                    msg_data = message.value
                    
                    if not msg_data.get('valid', False):
                        # Route to DLQ
                        dlq_message = {
                            'original_message': msg_data,
                            'error_reason': 'Validation failed',
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'retry_count': 0
                        }
                        
                        dlq_producer.send('market-data-dlq-test', value=dlq_message)
                        dlq_count += 1
                    else:
                        # Process normally
                        processed_count += 1
                    
                    if processed_count + dlq_count >= 5:
                        break
                        
                except Exception as e:
                    # Any processing error also goes to DLQ
                    dlq_message = {
                        'original_message': message.value,
                        'error_reason': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'retry_count': 0
                    }
                    dlq_producer.send('market-data-dlq-test', value=dlq_message)
                    dlq_count += 1
            
            dlq_producer.flush()
            
            # Verify DLQ handling
            assert processed_count == 3, f"Expected 3 valid messages, processed {processed_count}"
            assert dlq_count == 2, f"Expected 2 DLQ messages, routed {dlq_count}"
            
            # Verify DLQ messages
            dlq_consumer = KafkaConsumer(
                'market-data-dlq-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='traider-test-dlq-reader',
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            dlq_messages = []
            for message in dlq_consumer:
                dlq_messages.append(message.value)
                if len(dlq_messages) >= 2:
                    break
            
            assert len(dlq_messages) == 2, f"Expected 2 DLQ messages, found {len(dlq_messages)}"
            
            for dlq_msg in dlq_messages:
                assert 'original_message' in dlq_msg
                assert 'error_reason' in dlq_msg
                assert 'timestamp' in dlq_msg
            
            dlq_consumer.close()
            consumer.close()
            
        finally:
            producer.close()
            dlq_producer.close()
            admin_client.close()

    # =============================================================================
    # CROSS-SERVICE COMMUNICATION TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_cross_service_messaging_patterns(self, setup_kafka_infrastructure):
        """
        Test cross-service messaging patterns for trading system.
        
        @description
        Tests messaging patterns between trading services including
        request-response, publish-subscribe, and event streaming.
        
        @performance Target: <10ms end-to-end latency
        @tradingImpact Cross-service communication affects trading flow
        @riskLevel HIGH - Communication failures affect trading system
        """
        # Simulate market data -> signal generation -> order execution flow
        
        # Market data producer (simulates market data service)
        market_producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # Signal producer (simulates signal generation service)
        signal_producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        # Order producer (simulates order execution service)
        order_producer = KafkaProducer(
            bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        try:
            # Step 1: Market data service publishes market data
            market_data = {
                'symbol': 'BTC-USD',
                'price': 50000.0,
                'volume': 1.5,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'correlation_id': str(uuid.uuid4())
            }
            
            start_time = time.time()
            market_producer.send('market-data-test', value=market_data)
            market_producer.flush()
            
            # Step 2: Signal generation service consumes market data and produces signal
            market_consumer = KafkaConsumer(
                'market-data-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='signal-generation-service',
                auto_offset_reset='latest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            # Consume market data and generate signal
            for message in market_consumer:
                received_data = message.value
                
                # Generate trading signal
                signal = {
                    'signal_id': str(uuid.uuid4()),
                    'symbol': received_data['symbol'],
                    'signal_type': 'buy',
                    'strength': 0.8,
                    'source_correlation_id': received_data['correlation_id'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                signal_producer.send('trading-signals-test', value=signal)
                signal_producer.flush()
                break
            
            # Step 3: Order execution service consumes signal and executes order
            signal_consumer = KafkaConsumer(
                'trading-signals-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='order-execution-service',
                auto_offset_reset='latest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            for message in signal_consumer:
                received_signal = message.value
                
                # Execute order
                order = {
                    'order_id': str(uuid.uuid4()),
                    'symbol': received_signal['symbol'],
                    'side': received_signal['signal_type'],
                    'quantity': 0.1,
                    'order_type': 'market',
                    'signal_correlation_id': received_signal['source_correlation_id'],
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
                order_producer.send('order-execution-test', value=order)
                order_producer.flush()
                break
            
            end_time = time.time()
            total_latency = (end_time - start_time) * 1000
            
            # Verify end-to-end flow
            order_consumer = KafkaConsumer(
                'order-execution-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='order-verification',
                auto_offset_reset='latest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            executed_order = None
            for message in order_consumer:
                executed_order = message.value
                break
            
            # Verify complete flow
            assert executed_order is not None, "Order was not executed"
            assert executed_order['symbol'] == 'BTC-USD'
            assert executed_order['side'] == 'buy'
            assert 'signal_correlation_id' in executed_order
            
            # Performance check
            assert total_latency < 1000, f"End-to-end latency {total_latency:.2f}ms, expected <1000ms"
            
            # Cleanup consumers
            market_consumer.close()
            signal_consumer.close()
            order_consumer.close()
            
        finally:
            market_producer.close()
            signal_producer.close()
            order_producer.close()

    # =============================================================================
    # MONITORING AND METRICS TESTS
    # =============================================================================

    @pytest.mark.asyncio
    async def test_kafka_monitoring_and_metrics(self, setup_kafka_infrastructure):
        """
        Test Kafka monitoring and metrics collection.
        
        @description
        Tests monitoring capabilities for Kafka infrastructure
        including consumer lag, throughput metrics, and health monitoring.
        
        @performance Target: Real-time metrics collection
        @tradingImpact Monitoring critical for operational visibility
        @riskLevel MEDIUM - Monitoring affects incident response
        """
        # This test validates that we can collect Kafka metrics
        # In production, this would integrate with Prometheus/Grafana
        
        # Create admin client for metrics
        admin_client = KafkaAdminClient(bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS)
        
        try:
            # Get cluster metadata
            metadata = admin_client.describe_cluster()
            
            # Verify cluster is healthy
            assert len(metadata.brokers) > 0, "No Kafka brokers available"
            
            # Test topic metrics
            topics = admin_client.list_topics()
            test_topics = [topic for topic in self.TEST_TOPICS if topic in topics]
            assert len(test_topics) > 0, "No test topics found"
            
            # Producer metrics test
            producer = KafkaProducer(
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            
            # Send some messages to generate metrics
            for i in range(10):
                message = {'metric_test': i, 'timestamp': datetime.now(timezone.utc).isoformat()}
                producer.send('market-data-test', value=message)
            
            producer.flush()
            
            # Get producer metrics
            producer_metrics = producer.metrics()
            
            # Verify key metrics are available
            assert 'producer-metrics' in producer_metrics
            assert any('record-send-rate' in metric for metric in producer_metrics.keys())
            
            producer.close()
            
            # Consumer lag test
            consumer = KafkaConsumer(
                'market-data-test',
                bootstrap_servers=self.KAFKA_BOOTSTRAP_SERVERS,
                group_id='traider-test-metrics-consumer',
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            # Consume some messages
            consumed = 0
            for message in consumer:
                consumed += 1
                if consumed >= 5:
                    break
            
            # Get consumer metrics
            consumer_metrics = consumer.metrics()
            
            # Verify consumer metrics
            assert 'consumer-metrics' in consumer_metrics
            assert any('records-consumed-rate' in metric for metric in consumer_metrics.keys())
            
            consumer.close()
            
        finally:
            admin_client.close() 