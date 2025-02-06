# RSS [Retrieval Semantic Search]
### Retrieval Semantic Search
Used for finding a logical segments of texts in a big text corpora.
Originally designed for russian texts, but you can use different models and prompts, since that's all you need.
Initially, this was the module of a system with agents, tools etc, so consider this as a start point for your needs.

## What it does and how can I utilize it?
Suppose, you have a couple sentances with a brief explaination of some topic in some lecture and you wanna 
find the exact logically bounded chapter or paragraph. That is when RSS can shine as it based on RAG idea.
## How to use?
```python
python rss.py search --init <path> --syn <path> --output <path> --verbose
```
Note:  
For proper use, you may need to modify the logics of text file reading
