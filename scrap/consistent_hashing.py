import hashlib
import struct

HASH_IDX = 3

FIRST = 0
LAST = -1

class ConsistentHashingPartitioning:
    """
        멤버변수:
            continuum
            nodelist
            hash_func
            vnode_counts
        멤버함수:
            md5_hash
            add_node_to_ring
            remove_node_from_ring
            rebuild
            find_node_with_value
    """
    def __init__(self, nodelist, vnode_counts, hash_func = None):
        self.hash_func = hash_func
        if not self.hash_func:
            self.hash_func = self.md5_hash

        self.nodelist = nodelist
        self.vnode_counts = vnode_counts
        self.continuum = self.rebuild(nodelist)


    def md5_hash(self, key):
        return struct.unpack('>I', hashlib.md5(key.encode()).digest()[0:4])

    
    def rebuild(self, nodelist):
        continuum = [(hname, value, vnode, self._hash("%s:%s:%s" % (hname, value, vnode))) \
                for hname, value in nodelist \
                for vnode in range(self.vnode_counts) 
                ]
        continuum = sorted(continuum, key=(lambda item:item[HASH_IDX]))
        return continuum
    

    def _hash(self, key):
        return self.hash_func(key)

    
    def add_node_to_ring(self, node):
        self.nodelist.append(node)
        self.continuum = self.rebuild(self.nodelist)

    def remove_node_from_ring(self, node):
        self.nodelist.remove(node)
        self.continuum = self.rebuild(self.nodelist)

    
    def find_node_with_value(self, value):
        hash = self._hash(value)
        if hash > self.continuum[LAST][HASH_IDX]: # hash값이 마지막 노드의 해시값보다 크다면 제일 첫번쨰 노드로 간다.
            return self.continuum[FIRST]
        else: #그렇지 않으면 두번째 노드부터해서 hash보다 값이 큰 노드의 해시중 가장 근접한 노드로 간다.
            i = FIRST
            while hash > self.continuum[i][HASH_IDX]:
                i += 1
            return self.continuum[i]

