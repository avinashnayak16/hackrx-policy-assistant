import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')

PROMPT_TEMPLATE = '''You are a domain-aware policy assistant.
User question: {question}

You are given the following candidate clauses with metadata:
{clauses}

Task:
1. Provide a short concise answer (1-3 sentences) to the user's question as it pertains to the provided clauses.
2. Provide a stepwise reasoning of how you arrived at the answer.
3. Return any clause text that clearly supports the answer as sources (up to top 3), with page numbers and similarity scores.

If clauses conflict or are ambiguous, state that you are unsure and list conflicting clauses.

Output JSON with keys: answer, reasoning, sources (list of {{text,page,score}})
'''

def synthesize_answer(question, clauses):
    # build clause string
    clause_text = '\n'.join([f"- (score={c['score']:.3f}) page={c['meta'].get('page')} id={c['id']} text={c['meta'].get('text') or c['text'][:200]}" for c in clauses[:6]])
    prompt = PROMPT_TEMPLATE.format(question=question, clauses=clause_text)
    # call chat completion
    resp = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role':'system','content':'You are an expert insurance policy analyst.'},
                  {'role':'user','content':prompt}],
        max_tokens=512,
        temperature=0.0
    )
    content = resp['choices'][0]['message']['content']

    # Expect JSON in content; try to parse gracefully
    import json
    try:
        parsed = json.loads(content)
    except Exception:
        # fallback: wrap content
        parsed = {"answer": content, "reasoning": "(auto-parsed)", "sources": []}
    return parsed