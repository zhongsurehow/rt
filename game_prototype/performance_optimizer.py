#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天机变游戏性能优化系统
Performance Optimization System for TianJiBian Game
"""

import time
import functools
import threading
import weakref
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import json
import os

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    function_name: str
    execution_time: float
    memory_usage: int
    call_count: int
    timestamp: float

class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetrics]] = {}
        self.cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._lock = threading.Lock()
        
    def profile(self, func_name: str = None):
        """性能分析装饰器"""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = self._get_memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_memory = self._get_memory_usage()
                    
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    metric = PerformanceMetrics(
                        function_name=name,
                        execution_time=execution_time,
                        memory_usage=memory_delta,
                        call_count=1,
                        timestamp=end_time
                    )
                    
                    with self._lock:
                        if name not in self.metrics:
                            self.metrics[name] = []
                        self.metrics[name].append(metric)
                        
                        # 保持最近100次调用记录
                        if len(self.metrics[name]) > 100:
                            self.metrics[name] = self.metrics[name][-100:]
            
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> int:
        """获取内存使用量（简化版）"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            "cache_stats": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_ratio": self.cache_hits / max(1, self.cache_hits + self.cache_misses)
            },
            "function_stats": {}
        }
        
        for func_name, metrics_list in self.metrics.items():
            if not metrics_list:
                continue
                
            total_time = sum(m.execution_time for m in metrics_list)
            avg_time = total_time / len(metrics_list)
            max_time = max(m.execution_time for m in metrics_list)
            min_time = min(m.execution_time for m in metrics_list)
            
            report["function_stats"][func_name] = {
                "call_count": len(metrics_list),
                "total_time": total_time,
                "average_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "recent_calls": metrics_list[-5:]  # 最近5次调用
            }
        
        return report

class GameCache:
    """游戏数据缓存系统"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self._lock:
            if key in self._cache:
                self._access_times[key] = time.time()
                return self._cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[key] = value
            self._access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """移除最旧的缓存项"""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), 
                        key=lambda k: self._access_times[k])
        del self._cache[oldest_key]
        del self._access_times[oldest_key]
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

class LazyLoader:
    """延迟加载器"""
    
    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._loading_lock = threading.Lock()
    
    def load_module(self, module_name: str, loader_func: Callable) -> Any:
        """延迟加载模块"""
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        with self._loading_lock:
            # 双重检查锁定
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            module = loader_func()
            self._loaded_modules[module_name] = module
            return module
    
    def get_load_status(self) -> Dict[str, Any]:
        """获取加载状态"""
        return {
            "loaded_modules": list(self._loaded_modules.keys()),
            "module_count": len(self._loaded_modules),
            "memory_usage": sum(sys.getsizeof(module) for module in self._loaded_modules.values())
        }

class PerformanceOptimizer:
    """性能优化器主类"""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self.cache = GameCache()
        self.lazy_loader = LazyLoader()
        self.optimization_enabled = True
        
    def enable_optimization(self) -> None:
        """启用性能优化"""
        self.optimization_enabled = True
        print("🚀 性能优化已启用")
    
    def disable_optimization(self) -> None:
        """禁用性能优化"""
        self.optimization_enabled = False
        print("⏸️ 性能优化已禁用")
    
    def cached_function(self, cache_key_func: Callable = None):
        """缓存函数结果的装饰器"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.optimization_enabled:
                    return func(*args, **kwargs)
                
                # 生成缓存键
                if cache_key_func:
                    cache_key = cache_key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # 尝试从缓存获取
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    self.profiler.cache_hits += 1
                    return cached_result
                
                # 执行函数并缓存结果
                self.profiler.cache_misses += 1
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result)
                return result
            
            return wrapper
        return decorator
    
    def batch_process(self, items: List[Any], process_func: Callable, 
                     batch_size: int = 50) -> List[Any]:
        """批量处理优化"""
        if not self.optimization_enabled:
            return [process_func(item) for item in items]
        
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = [process_func(item) for item in batch]
            results.extend(batch_results)
            
            # 让出CPU时间片
            if i + batch_size < len(items):
                time.sleep(0.001)
        
        return results
    
    def optimize_game_state_updates(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """优化游戏状态更新"""
        if not self.optimization_enabled:
            return game_state
        
        # 只更新变化的部分
        optimized_state = {}
        
        # 缓存常用计算结果
        cache_key = f"game_state:{hash(str(game_state))}"
        cached_state = self.cache.get(cache_key)
        
        if cached_state:
            return cached_state
        
        # 执行优化逻辑
        optimized_state = self._deep_copy_optimized(game_state)
        self.cache.set(cache_key, optimized_state)
        
        return optimized_state
    
    def _deep_copy_optimized(self, obj: Any) -> Any:
        """优化的深拷贝"""
        if isinstance(obj, dict):
            return {k: self._deep_copy_optimized(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy_optimized(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._deep_copy_optimized(item) for item in obj)
        else:
            return obj
    
    def save_performance_report(self, filename: str = "performance_report.json") -> None:
        """保存性能报告"""
        report = self.profiler.get_performance_report()
        report["cache_size"] = self.cache.size()
        report["optimization_enabled"] = self.optimization_enabled
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📊 性能报告已保存到: {filepath}")
    
    def print_performance_summary(self) -> None:
        """打印性能摘要"""
        report = self.profiler.get_performance_report()
        
        print("\n" + "="*50)
        print("🎯 天机变游戏性能报告")
        print("="*50)
        
        # 缓存统计
        cache_stats = report["cache_stats"]
        print(f"📦 缓存统计:")
        print(f"   命中次数: {cache_stats['hits']}")
        print(f"   未命中次数: {cache_stats['misses']}")
        print(f"   命中率: {cache_stats['hit_ratio']:.2%}")
        print(f"   缓存大小: {self.cache.size()}")
        
        # 函数性能统计
        print(f"\n⚡ 函数性能统计:")
        func_stats = report["function_stats"]
        
        if func_stats:
            # 按平均执行时间排序
            sorted_funcs = sorted(func_stats.items(), 
                                key=lambda x: x[1]["average_time"], 
                                reverse=True)
            
            for func_name, stats in sorted_funcs[:10]:  # 显示前10个最慢的函数
                print(f"   {func_name}:")
                print(f"     调用次数: {stats['call_count']}")
                print(f"     平均时间: {stats['average_time']:.4f}s")
                print(f"     总时间: {stats['total_time']:.4f}s")
                print(f"     最大时间: {stats['max_time']:.4f}s")
        else:
            print("   暂无函数性能数据")
        
        print("="*50)

# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()

# 便捷装饰器
profile = performance_optimizer.profiler.profile
cached = performance_optimizer.cached_function

def optimize_imports():
    """优化导入性能"""
    import sys
    
    # 预编译常用模块
    common_modules = [
        'json', 'time', 'random', 'copy', 'itertools',
        'collections', 'functools', 'threading'
    ]
    
    for module_name in common_modules:
        if module_name not in sys.modules:
            try:
                __import__(module_name)
            except ImportError:
                pass

def create_performance_test():
    """创建性能测试"""
    
    @profile("test_function")
    def test_function():
        time.sleep(0.01)  # 模拟计算
        return "test_result"
    
    @cached()
    def cached_calculation(n):
        time.sleep(0.005)  # 模拟复杂计算
        return n * n
    
    print("🧪 运行性能测试...")
    
    # 测试普通函数
    for i in range(10):
        test_function()
    
    # 测试缓存函数
    for i in range(5):
        cached_calculation(i)
    
    # 重复调用测试缓存效果
    for i in range(5):
        cached_calculation(i % 3)
    
    performance_optimizer.print_performance_summary()

if __name__ == "__main__":
    print("🚀 天机变游戏性能优化系统")
    print("正在初始化性能优化...")
    
    optimize_imports()
    create_performance_test()
    
    performance_optimizer.save_performance_report()