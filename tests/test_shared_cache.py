"""Run with the affected EXL3 environment; argv[1] is the module source path."""
import importlib.util
import sys
import torch
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit('Usage: python test_shared_cache.py /path/to/model_tp_shared.py')
source = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('exllamav3.model.incident_shared_test', source)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.MAX_CACHE_PER_PROCESS = 2 * 1024 * 1024
producer = m.SMProducer(buffer_size=4 * 1024 * 1024)
consumer = m.SMConsumer.__new__(m.SMConsumer)
consumer.cached_cpu_tensors = {}
consumer.cache_size = 0
consumer.arena = torch.from_numpy(producer.buf)
try:
    for i in range(40):
        producer.clear()
        tensor = torch.full((256 * 1024,), i, dtype=torch.float32)
        result = consumer.recv(producer.send(tensor, cache_id=i))
        assert torch.equal(result, tensor)
        for obj in (producer, consumer):
            actual = sum(v.numel() * v.element_size() for v in obj.cached_cpu_tensors.values())
            assert obj.cache_size == actual, (type(obj).__name__, obj.cache_size, actual)
            assert actual <= m.MAX_CACHE_PER_PROCESS
        assert list(producer.cached_cpu_tensors) == list(consumer.cached_cpu_tensors)
    producer.clear()
    cached = producer.send(tensor, cache_id=39)
    assert cached['method'] == 'cached'
    assert torch.equal(consumer.recv(cached), tensor)
    print('PASS: 40 transfers, exact values, bounded FIFO eviction, synchronized byte accounting, cache reuse')
finally:
    del consumer.arena
    producer.close()
