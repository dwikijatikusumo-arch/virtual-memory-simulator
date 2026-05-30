from collections import OrderedDict
from typing import List, Dict, Any

class PageReplacement:
    """Implementasi algoritma penggantian halaman untuk web service"""
    
    @staticmethod
    def fifo(pages: List[int], frames: int) -> tuple:
        """First-In-First-Out dengan step-by-step tracking"""
        memory = []
        page_faults = 0
        steps = []
        
        for page in pages:
            fault = False
            if page not in memory:
                fault = True
                page_faults += 1
                if len(memory) < frames:
                    memory.append(page)
                else:
                    memory.pop(0)
                    memory.append(page)
            steps.append({
                "page": page,
                "memory": memory.copy(),
                "fault": fault
            })
        return page_faults, steps
    
    @staticmethod
    def lru(pages: List[int], frames: int) -> tuple:
        """Least Recently Used dengan OrderedDict"""
        memory = OrderedDict()
        page_faults = 0
        steps = []
        
        for page in pages:
            fault = False
            if page not in memory:
                fault = True
                page_faults += 1
                if len(memory) >= frames:
                    memory.popitem(last=False)
                memory[page] = True
            else:
                memory.move_to_end(page)
            steps.append({
                "page": page,
                "memory": list(memory.keys()),
                "fault": fault
            })
        return page_faults, steps
    
    @staticmethod
    def optimal(pages: List[int], frames: int) -> tuple:
        """Optimal (MIN) algorithm - melihat future access"""
        memory = []
        page_faults = 0
        steps = []
        
        for i, page in enumerate(pages):
            fault = False
            if page not in memory:
                fault = True
                page_faults += 1
                if len(memory) < frames:
                    memory.append(page)
                else:
                    future = pages[i+1:]
                    victim = None
                    farthest = -1
                    
                    for p in memory:
                        if p not in future:
                            victim = p
                            break
                        else:
                            idx = future.index(p)
                            if idx > farthest:
                                farthest = idx
                                victim = p
                    
                    if victim is not None:
                        memory[memory.index(victim)] = page
            steps.append({
                "page": page,
                "memory": memory.copy(),
                "fault": fault
            })
        return page_faults, steps


def detect_thrashing(page_faults: int, total_pages: int, threshold: float = 0.9) -> Dict[str, Any]:
    """Deteksi potensi thrashing berdasarkan page fault rate"""
    fault_rate = page_faults / total_pages if total_pages > 0 else 0
    return {
        "fault_rate": round(fault_rate, 4),
        "is_thrashing": fault_rate > threshold,
        "severity": "High" if fault_rate > 0.95 else "Medium" if fault_rate > 0.85 else "Low"
    }
