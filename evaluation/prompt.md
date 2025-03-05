Evaluate the quality of answers from multiple Question Answering systems. 

### Input format:

Questions and answers are provided in the following format:

Question:

{question}

Answer 1: ChatTogoVar

{chat_togovar}

Answer2: GPT-4o

{chat_gpt}

Answer3: VarChat

{varchat}

### Gold standard

Gene symbols: {gene_symbols}

### Evaluation Criteria:
	1.	Accuracy: How accurately does the response address the question? Point out any inaccuracies or missing information. Please refer to the gene symbols in the 'Gold standard' above as the correct genes in which the variant mentioned in the question is located.
	2.	Completeness: Does the response itself provide all the necessary information required to fully answer the question, rather than just pointing to potential sources? Highlight any gaps where specific details should have been provided.
	3.	Logical Consistency: Does the response maintain logical coherence, with no contradictions?
	4.	Clarity and Conciseness: Is the response clear and concise, with no ambiguity? Identify any overly verbose or unclear sections.
	5.	Evidence Support: Does the response rely on credible sources or evidence? Note if the support provided is insufficient or untrustworthy.

### Instructions:

Please provide the evaluation output in the exact format specified below. 

- Follow the exact structure and formatting of the "Output Format" section.
- Do not add or remove any symbols (e.g., colons, bullet points, spaces).
- Ensure the alignment and indentation are consistent with the "Output Format."
- Replace "X" with the appropriate value or text based on the evaluation.
- If "Reason" is not applicable, write "Not provided" but keep the "Reason" line in the output.
- Every reason should be written in both English and Japanese.

Only output in this format. Do not include additional text or explanations outside of the format.

### Output Format:

## Question

{question}

## Final Result

- Best Answer: X
- Total Score for ChatTogoVar: X/50
- Total Score for GPT-4o: X/50
- Total Score for VarChat: X/50
- Reason:
  - English: X
  - 日本語: X

---

## Scores by Evaluation Criteria

### Answer ChatTogoVar
- Accuracy Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Completeness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Logical Consistency Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Clarity and Conciseness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Evidence Support Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Total Score: X/50

---

### Answer GPT-4o
- Accuracy Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Completeness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Logical Consistency Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Clarity and Conciseness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Evidence Support Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Total Score: X/50

---

### Answer VarChat
- Accuracy Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Completeness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Logical Consistency Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Clarity and Conciseness Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Evidence Support Score: X/10
  - Reason: 
    - English: X
    - 日本語: X
- Total Score: X/50
