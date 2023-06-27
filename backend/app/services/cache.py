import weakref


class Cache:
    class Element(object):
        __slots__ = ['prev', 'next', 'value', '__weakref__']

        def __init__(self, value):
            self.prev, self.next, self.value = None, None, value

    def __init__(self, max_count):
        self.dict = weakref.WeakValueDictionary()
        self.head = None
        self.tail = None
        self.count = 0
        self.maxCount = max_count

    def _remove_element(self, element):
        prev, next = element.prev, element.next
        if prev:
            assert prev.next == element
            prev.next = next
        elif self.head == element:
            self.head = next

        if next:
            assert next.prev == element
            next.prev = prev
        elif self.tail == element:
            self.tail = prev
        element.prev, element.next = None, None
        assert self.count >= 1
        self.count -= 1

    def _append_element(self, element):
        if element is None:
            return
        element.prev, element.next = self.tail, None
        if self.head is None:
            self.head = element
        if self.tail is not None:
            self.tail.next = element
        self.tail = element
        self.count += 1

    def get(self, key):
        element = self.dict.get(key, None)
        if element:
            self._remove_element(element)
            self._append_element(element)
            return element.value
        else:
            return None

    def __len__(self):
        return len(self.dict)

    def __getitem__(self, key):
        element = self.dict[key]
        self._remove_element(element)
        self._append_element(element)
        return element.value

    def __setitem__(self, key, value):
        try:
            element = self.dict[key]
            self._remove_element(element)
        except KeyError:
            if self.count == self.maxCount:
                self._remove_element(self.head)
        element = Cache.Element(value)
        self._append_element(element)
        self.dict[key] = element

    def __del__(self):
        while self.head:
            self._remove_element(self.head)
