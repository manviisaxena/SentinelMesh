import json, os, time, threading, logging
import pika
log = logging.getLogger("sentinel.messaging")

def broker_url():
    if os.getenv("AMQP_URL"):
        return os.environ["AMQP_URL"]
    import urllib.parse
    user=urllib.parse.quote(os.getenv("RABBITMQ_USER", "guest"), safe="")
    password=urllib.parse.quote(os.getenv("RABBITMQ_PASSWORD", "guest"), safe="")
    host=os.getenv("RABBITMQ_HOST", "rabbitmq")
    return f"amqp://{user}:{password}@{host}:5672/%2F"
EXCHANGE = "sentinel.events"

def publish(routing_key, payload):
    params = pika.URLParameters(broker_url())
    params.socket_timeout = 3
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        channel.basic_publish(exchange=EXCHANGE, routing_key=routing_key,
            body=json.dumps(payload).encode(), properties=pika.BasicProperties(delivery_mode=2,
            content_type="application/json"), mandatory=False)
    finally:
        connection.close()

def consume(queue_name, routing_key, callback):
    """Reconnect forever. Callback must raise on failure so RabbitMQ can requeue."""
    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(pika.URLParameters(broker_url()))
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(queue=queue_name, exchange=EXCHANGE, routing_key=routing_key)
            channel.basic_qos(prefetch_count=1)
            def wrapped(ch, method, props, body):
                try:
                    callback(json.loads(body.decode()))
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:
                    log.exception("Message processing failed; requeueing")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            channel.basic_consume(queue=queue_name, on_message_callback=wrapped)
            log.info("Consuming %s (%s)", queue_name, routing_key)
            channel.start_consuming()
        except Exception:
            log.exception("Consumer connection failed; retrying in 3s")
            time.sleep(3)
        finally:
            try:
                if connection and connection.is_open: connection.close()
            except Exception: pass

def start_consumer(queue_name, routing_key, callback):
    thread = threading.Thread(target=consume, args=(queue_name, routing_key, callback), daemon=True)
    thread.start()
    return thread
