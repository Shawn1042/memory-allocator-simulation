from typing import List, Tuple

class FixedBufferAllocator:
    def __init__(self, buffer_size: int):
        """
        Initialize a fixed-size memory buffer allocator.

        :param buffer_size: Total size of the memory buffer.
        """
        self.buffer = [None] * buffer_size
        self.allocations: List[Tuple[int, int]] = []
        self.free_blocks: List[Tuple[int, int]] = [(0, buffer_size)]

    def allocate(self, size: int) -> int:
        """
        Allocate a block of memory of the given size.

        :param size: Size of the memory block to allocate.
        :return: Starting index of the allocated block.
        :raises ValueError: If size is invalid.
        :raises MemoryError: If no suitable block is available.
        """
        if size <= 0:
            raise ValueError("Size must be greater than 0")
        if size > self.buffer_size:
            raise MemoryError("Requested size exceeds buffer capacity")

        # Binary search for free block
        left, right = 0, len(self.free_blocks) - 1
        while left <= right:
            mid = (left + right) // 2
            start, block_size = self.free_blocks[mid]
            if block_size >= size:
                if mid == 0 or self.free_blocks[mid-1][1] < size:
                    # Found suitable block
                    break
                right = mid - 1
            else:
                left = mid + 1
        else:
            raise MemoryError("Out of memory")

        start, block_size = self.free_blocks[mid]
        if block_size == size:
            self.free_blocks.pop(mid)
        else:
            self.free_blocks[mid] = (start + size, block_size - size)
        
        self.allocations.append((start, size))
        return start

    def free(self, ptr: int) -> None:
        """
        Free the memory block starting at the given pointer.

        :param ptr: Starting index of the block to free.
        :raises ValueError: If the pointer is invalid.
        """
        if not 0 <= ptr < len(self.buffer):
            raise ValueError("Invalid pointer")

        for i, (start, size) in enumerate(self.allocations):
            if start == ptr:
                self.allocations.pop(i)
                self.free_blocks.append((ptr, size))
                self._defragment_if_needed()
                return
        raise ValueError("Invalid pointer")

    def _defragment_if_needed(self) -> None:
        """Defragment memory if necessary."""
        if len(self.free_blocks) > len(self.allocations) * 2:  # Example threshold
            self.defragment()

    def defragment(self) -> None:
        """Merge adjacent free blocks."""
        self.free_blocks.sort()
        i = 0
        while i < len(self.free_blocks) - 1:
            current, next_block = self.free_blocks[i], self.free_blocks[i+1]
            if current[0] + current[1] == next_block[0]:
                merged = (current[0], current[1] + next_block[1])
                self.free_blocks[i] = merged
                self.free_blocks.pop(i+1)
            else:
                i += 1

    def print_memory(self) -> None:
        """Print the current state of memory allocations."""
        print("Memory buffer:", self.buffer)
        print("Allocations:", self.allocations)
        print("Free blocks:", self.free_blocks)

    @property
    def buffer_size(self) -> int:
        """Return the total size of the buffer."""
        return len(self.buffer)