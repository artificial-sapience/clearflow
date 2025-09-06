"""Type stubs for faiss-cpu.

Minimal stubs for the subset of FAISS used in ClearFlow examples.
"""

import numpy as np
import numpy.typing as npt


class Index:
    """Base class for FAISS indices."""
    
    ntotal: int
    
    def add(self, x: npt.NDArray[np.float32]) -> None:
        """Add vectors to the index."""
        ...
    
    def search(
        self, x: npt.NDArray[np.float32], k: int
    ) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.int64]]:
        """Search for k nearest neighbors.
        
        Returns:
            Tuple of (distances, indices)
        """
        ...


class IndexFlatL2(Index):
    """Flat index with L2 distance."""
    
    def __init__(self, d: int) -> None:
        """Initialize index with dimension d."""
        ...