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
        """
        Constructor with layerStore represented with ArrayStack ADT of element
        size 1, as only one layer can be stored in the SetLayerStore
        var: is_special is used to toggle the special()
        :complexity:
        Best & Worse case: O(1), constant time
        """
        super().__init__()
        self.layerStack = ArrayStack(1)
        self.is_special = False

    def add(self, layer: Layer) -> bool:
        """
        Set the single layer into the layerStore
        :complexity:
        Best & Worse case: O(1), constant time
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
        """
        Apply the layer that is on the Stack
        If is_special(), apply invert layer
        :complexity:
        Best & Worse case: O(1), constant time
        """
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
        :complexity:
        Best & Worse case: O(1), constant time
        """
        if self.layerStack.is_full():
            self.layerStack.pop()
            return True
        else:
            return False

    def special(self):
        """
        Invert the colour output. Toggles, the boolean var is_special
        :complexity:
        Best & Worse cast: O(1), constant time
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
        """
        In the constructor, 2 CircularQueue are used for additive
        AdditiveLayerStore uses the circularqueue due to the nature of add
        , erase, and special(), where the oldest layer gets removed out of
        the layerStore first until it reaches the newly added layer
        :complexity:
        Best & Worse Case: O(1)
        """
        super().__init__()
        self.layerCircularQueue = CircularQueue(2000)
        self.tempCircularQueue = CircularQueue(2000)

    def add(self, layer: Layer) -> bool:
        """
        Add a new layer to be added last
        :complexity:
        Best & Worse case: O(1), constant time
        """
        # If full and cannot add, return False
        if self.layerCircularQueue.is_full():
            return False
        else:
            self.layerCircularQueue.append(layer)
            return True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the layers that exists in the CircularQueue from the oldest
        layer first, then proceed to the last recently added layer.
        :complexity:
        Best Case: O(1), where the layerStore is empty.
        Worse Case: O(2000), where 2000 is the maximum number of layer the
                    layerStore data structure can hold.
        """
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
        """
        Remove the first layer that was added. Ignore what is currently selected.
        :complexity:
        Best & Worse Case: O(1), constant time
        """
        if self.layerCircularQueue.is_empty():
            return False
        else:
            # Remove the first layer added, return True
            self.layerCircularQueue.serve()
            return True

    def special(self):
        """
        Reverse the order of current layers (first becomes last, etc.)
        :complexity:
        Best Case: O(1), where the queue is empty
        Worse Case: O(2 * n), where n is the number of elements in the
                    data structure. Becomes O(n) after omit.
        """
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
        """
        Constructor has variable ArraySortedList as the layer store.
        The ADT used for SequenceLayerStore will be ArraySortedList due
        to the nature of layer store to be sorted by its index, and also
        the requirement of special() method to lexicographically
        sort the layer store.
        :complexity:
        Best & Worse case: O(1), constant time
        """
        super().__init__()
        self.layerArr = ArraySortedList(len(get_layers()))

    def add(self, layer: Layer) -> bool:
        """
        Ensure this layer type is applied.
        :complexity:
        Best & Worse case: O(1), constant time
        """
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
        """
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
        :complexity:
        Best case: O(1), where the array is empty.
        Worse case: O(n * m), where n is the number of elements in the array that
                    is "applying", where m is the array in get_layers()
        """
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
        """
        Ensure this layer type is not applied.
        :complexity:
        Best & Worse case: O(1), constant time
        """
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
        """
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
        :complexity:
        Best case: O(1), where the layer store is empty
        Worse case: O(n), where n is the number of layers in the layer store.
        """
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

