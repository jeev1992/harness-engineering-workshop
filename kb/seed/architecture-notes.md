# Architecture Notes

The knowledge base stores source documents separately from its metadata index.
Derived state must be reconciled whenever a source document changes.

The retrieval path ranks individual lines by token overlap and returns the
source document identifier with every matching line.

