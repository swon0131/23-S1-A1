from __future__ import annotations
from abc import ABC, abstractmethod

import layers
from data_structures.bset import BSet
from data_structures.sorted_list_adt import ListItem
from data_structures.array_sorted_list import ArraySortedList
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from layer_util import Layer, get_layers
from layers import *


class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass


class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """

    def __init__(self):
        super().__init__()
        self.layerStack = ArrayStack(1)
        self.is_special = False

    def add(self, layer: Layer) -> bool:
        """
        Set the single layer
        """
        # Check if full
        if self.layerStack.is_full():
            # If the added layer is the same as applied, return False
            if self.layerStack.peek() == layer:
                return False
            else:
                self.layerStack.pop()
        self.layerStack.push(layer)
        return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        if self.layerStack.is_full():  # Stack has layer
            if self.is_special:
                # Apply the layer and then invert
                current_layer = self.layerStack.peek().apply(start, timestamp, x, y)
                return invert.apply(current_layer, timestamp, x, y)
            # Apply the layer
            return self.layerStack.peek().apply(start, timestamp, x, y)
        else:  # Stack has no layer
            if self.is_special:
                # If is_special, invert start
                return invert.apply(start, timestamp, x, y)
            else:
                return start

    def erase(self, layer: Layer) -> bool:
        """
        Remove the single layer. Ignore what is currently selected.
        """
        if self.layerStack.is_full():
            self.layerStack.pop()
            return True
        else:
            return False

    def special(self):
        """
        Invert the colour output.
        """
        # special() toggles the is_special boolean
        if self.is_special:
            self.is_special = False
        elif not self.is_special:
            self.is_special = True


class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    def __init__(self):
        super().__init__()
        self.layerCircularQueue = CircularQueue(2000)
        self.tempCircularQueue = CircularQueue(2000)

    def add(self, layer: Layer) -> bool:
        # If full and cannot add, return False
        if self.layerCircularQueue.is_full():
            return False
        else:
            self.layerCircularQueue.append(layer)
            return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        if self.layerCircularQueue.is_empty():
            return start
        else:
            if not self.layerCircularQueue.is_empty():
                while not self.layerCircularQueue.is_empty():
                    layer = self.layerCircularQueue.serve()
                    self.tempCircularQueue.append(layer)
                    start = layer.apply(start, timestamp, x, y)
                while not self.tempCircularQueue.is_empty():
                    self.layerCircularQueue.append(self.tempCircularQueue.serve())
            return start

    def erase(self, layer: Layer) -> bool:
        if self.layerCircularQueue.is_empty():
            return False
        else:
            # Remove the first layer added, return True
            self.layerCircularQueue.serve()
            return True

    def special(self):
        # Make sure the layer store is not empty
        if not self.layerCircularQueue.is_empty():
            layerStack = ArrayStack(self.layerCircularQueue.length)

            # Load Stack with layer
            while not self.layerCircularQueue.is_empty():
                layerStack.push(self.layerCircularQueue.serve())

            # Pop the stack into a new CircularQueue to imitate a reversed order
            while not layerStack.is_empty():
                self.layerCircularQueue.append(layerStack.pop())


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    def __init__(self):
        super().__init__()
        self.layerArr = ArraySortedList(len(get_layers()))
        self.layerSet = BSet(len(get_layers()))

    def add(self, layer: Layer) -> bool:
        if self.layerArr.is_full():
            # If array is full, return False
            return False
        elif not self.layerArr.__contains__(ListItem(True, layer.index)):
            # Add the layer if it is not yet added, return True
            self.layerArr.add(ListItem(True, layer.index))
            return True
        elif self.layerArr.__contains__(ListItem(False, layer.index)):
            # Removes the False layer and add the True layer, return True
            self.layerArr.remove(ListItem(False, layer.index))
            self.layerArr.add(ListItem(True, layer.index))
            return True
        else:
            return False

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        if self.layerArr.is_empty():
            return start
        else:
            for element in self.layerArr:
                if element is not None and element.value is True:
                    for layer_item in get_layers():
                        if layer_item is not None and layer_item.index is element.key:
                            start = layer_item.apply(start, timestamp, x, y)
            return start

    def erase(self, layer: Layer) -> bool:
        if self.layerArr.is_empty():
            # If array is empty, return False
            return False
        elif self.layerArr.__contains__((ListItem(True, layer.index))):
            # Array contains layer
            # Remove True attribute and add False attribute to layer
            self.layerArr.remove(ListItem(True, layer.index))
            self.layerArr.add(ListItem(False, layer.index))
            return True
        else:
            return False

    def special(self):
        if not self.layerArr.is_empty():
            # Arrange the array in lexicographic ordering into lexiArr from layerArr
            lexiArr = ArraySortedList(len(self.layerArr))
            for index in self.layerArr:
                # Check if element is not None and element is True(applying)
                if index is not None and index.value is True:
                    this_layer = None
                    for layer_item in get_layers():
                        if layer_item is not None and layer_item.index is index.key:
                            this_layer = layer_item
                    if index is not None and this_layer is not None:
                        lexiArr.add(ListItem(this_layer, this_layer.name))

            # Ensure the lexiArr is not empty before proceeding to execute special()
            if not lexiArr.is_empty():
                # Lexicographic ordering implemented.
                del_index = 0
                if len(lexiArr) > 1:
                    if len(lexiArr) % 2 == 0:
                        del_index = (len(lexiArr) // 2) - 1
                    else:
                        del_index = len(lexiArr) // 2

                # Find Median and erase median
                del_layer = lexiArr.__getitem__(del_index).value
                self.erase(del_layer)
                lexiArr.clear()


if __name__ == "__main__":
    print("void Main")
    s = SequenceLayerStore()

    print("Adding black and removing black")
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(black)
    s.add(rainbow)


    for item in s.layerArr:
        if item is not None:
            print(item)

