import React, { useState, useEffect } from 'react';
import { Octokit } from '@octokit/rest';
import { ScrollSync } from 'react-scroll-sync';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import JSON5 from 'json5';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';

function base64ToUtf8(base64) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return new TextDecoder().decode(bytes);
}

function utf8ToBase64(utf8String) {
  const bytes = new TextEncoder().encode(utf8String);
  let binary = '';
  bytes.forEach((b) => binary += String.fromCharCode(b));
  return btoa(binary);
}

function shuffle(array) {
  let currentIndex = array.length, randomIndex;
  while (currentIndex !== 0) {
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;
    [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
  }
  return array;
}

export default function AnswersEvaluator() {
  const [token, setToken] = useState('');
  const [filePairs, setFilePairs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fileContents, setFileContents] = useState(['', '', '']);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ A: {}, B: {}, C: {} });
  const [shuffledLabels, setShuffledLabels] = useState([]);
  const [questionText, setQuestionText] = useState('');

  useEffect(() => {
    const storedToken = localStorage.getItem('gh_token');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem('gh_token', token);
    }
  }, [token]);

  const octokit = new Octokit({ auth: token });

  const fetchFilePairs = async () => {
    const { data } = await octokit.repos.getContent({
      owner: 'mitsuhashi',
      repo: 'chat-togovar',
      path: 'answers/chat_togovar',
    });

    let pairs = [];
    for (const dir of data.filter(item => item.type === 'dir')) {
      const { data: files } = await octokit.repos.getContent({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path: `answers/chat_togovar/${dir.name}`
      });

      files.forEach(file => {
        if (file.name.endsWith('.md')) {
          const qY = dir.name;
          const rsXXXX = file.name;
          pairs.push({ qY, rsXXXX });
        }
      });
    }
    setFilePairs(pairs);
  };

  const fetchQuestion = async (qY, rs) => {
    const { data } = await octokit.request('GET /repos/mitsuhashi/chat-togovar/contents/questions.json');
    const content = base64ToUtf8(data.content);
    const questions = JSON5.parse(content);
    const qKey = qY;
    if (questions[qKey]) {
      const formatted = questions[qKey].replace('{rs}', rs);
      setQuestionText(formatted);
    } else {
      setQuestionText('Question template not found');
    }
  };

  const fetchFiles = async (pair) => {
    const paths = [
      { label: 'ChatTogoVar', path: `answers/chat_togovar/${pair.qY}/${pair.rsXXXX}` },
      { label: 'GPT-4o', path: `answers/gpt-4o/${pair.qY}/${pair.rsXXXX}` },
      { label: 'VarChat', path: `answers/varchat/${pair.rsXXXX}` },
    ];

    const rs = pair.rsXXXX.replace('.md', '');
    await fetchQuestion(pair.qY, rs);

    const shuffled = shuffle(['A', 'B', 'C'].map((k, i) => ({ key: k, label: paths[i].label, path: paths[i].path })));
    setShuffledLabels(shuffled);

    const contents = await Promise.all(shuffled.map(async (item) => {
      const { data } = await octokit.repos.getContent({
        owner: 'mitsuhashi', repo: 'chat-togovar', path: item.path
      });
      return base64ToUtf8(data.content);
    }));
    setFileContents(contents);
  };

  useEffect(() => {
    if (filePairs.length > 0) {
      fetchFiles(filePairs[currentIndex]);
    }
  }, [filePairs, currentIndex]);

  const handleInputChange = (key, field, subfield, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        [field]: {
          ...prev[key][field],
          [subfield]: value
        }
      }
    }));
  };

  const handleUpload = async () => {
    const path = `evaluation/human/evaluation_${filePairs[currentIndex].qY}_${filePairs[currentIndex].rsXXXX.replace('.md', '')}.jsonl`;
    let sha;
    try {
      const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
      sha = data.sha;
    } catch (err) {
      if (err.status !== 404) throw err;
    }

    const jsonlContent = JSON.stringify({
      ...filePairs[currentIndex],
      label_mapping: shuffledLabels.reduce((acc, item) => { acc[item.key] = item.label; return acc; }, {}),
      evaluation: form
    }) + '\n';
    const base64Content = utf8ToBase64(jsonlContent);

    try {
      await octokit.repos.createOrUpdateFileContents({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path,
        message: 'Add evaluation data',
        content: base64Content,
        sha: sha
      });
      setMessage('✅ Uploaded to GitHub!');
      setForm({ A: {}, B: {}, C: {} });
    } catch (error) {
      setMessage(`❌ Upload failed: ${error.message}`);
    }
  };

  return (
    <div className="p-4 space-y-6">
      <div className="flex flex-wrap gap-2">
        <Input placeholder="GitHub Token" value={token} onChange={(e) => setToken(e.target.value)} type="password" />
        <Button onClick={fetchFilePairs}>Load pairs</Button>
        <Button disabled={currentIndex <= 0} onClick={() => setCurrentIndex(currentIndex - 1)}>Previous</Button>
        <Button disabled={currentIndex >= filePairs.length - 1} onClick={() => setCurrentIndex(currentIndex + 1)}>Next</Button>
      </div>

      <div className="border p-4 bg-gray-50 rounded">
        <h2 className="font-bold">Question</h2>
        <p>{questionText}</p>
      </div>

      <ScrollSync>
        <div className="space-y-6">
          {/* Markdown display & scoring UI here */}
        </div>
      </ScrollSync>

      <div className="space-y-2">
        <Button onClick={handleUpload}>Upload Evaluation JSONL to GitHub</Button>
        {message && <p>{message}</p>}
      </div>
    </div>
  );
}
