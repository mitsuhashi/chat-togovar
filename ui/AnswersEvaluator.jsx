import React, { useState, useEffect } from 'react';
import { Octokit } from '@octokit/rest';
import { ScrollSync } from 'react-scroll-sync';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function AnswersEvaluator() {
  const [token, setToken] = useState('');
  const [filePairs, setFilePairs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fileContents, setFileContents] = useState(['', '', '']);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({
    chatTogoVar: {},
    gpt4o: {},
    varChat: {}
  });

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

  const fetchFiles = async (pair) => {
    const paths = [
      `answers/chat_togovar/${pair.qY}/${pair.rsXXXX}`,
      `answers/gpt-4o/${pair.qY}/${pair.rsXXXX}`,
      `answers/varchat/${pair.rsXXXX}`
    ];

    const contents = await Promise.all(paths.map(async (path) => {
      const { data } = await octokit.repos.getContent({
        owner: 'mitsuhashi', repo: 'chat-togovar', path
      });
      return atob(data.content);
    }));
    setFileContents(contents);
  };

  useEffect(() => {
    if (filePairs.length > 0) {
      fetchFiles(filePairs[currentIndex]);
    }
  }, [filePairs, currentIndex]);

  const handleInputChange = (section, field, subfield, value) => {
    setForm((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: {
          ...prev[section][field],
          [subfield]: value
        }
      }
    }));
  };

  const handleUpload = async () => {
    const jsonlContent = JSON.stringify({ ...filePairs[currentIndex], evaluation: form }) + '\n';
    const base64Content = btoa(unescape(encodeURIComponent(jsonlContent)));
    try {
      await octokit.repos.createOrUpdateFileContents({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path: `evaluation/human/evaluation_${filePairs[currentIndex].qY}_${filePairs[currentIndex].rsXXXX.replace('.md', '')}.jsonl`,
        message: 'Add evaluation data',
        content: base64Content
      });
      setMessage('✅ Uploaded to GitHub!');
      setForm({ chatTogoVar: {}, gpt4o: {}, varChat: {} });
    } catch (error) {
      setMessage(`❌ Upload failed: ${error.message}`);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex space-x-2">
        <Input placeholder="GitHub Token" value={token} onChange={(e) => setToken(e.target.value)} type="password" />
        <Button onClick={fetchFilePairs}>Load pairs</Button>
        <Button disabled={currentIndex <= 0} onClick={() => setCurrentIndex(currentIndex - 1)}>Previous</Button>
        <Button disabled={currentIndex >= filePairs.length - 1} onClick={() => setCurrentIndex(currentIndex + 1)}>Next</Button>
      </div>
      <ScrollSync>
        <div className="flex space-x-4">
          {fileContents.map((content, idx) => (
            <div key={idx} className="w-1/3 space-y-2">
              <div className="h-[70vh] overflow-auto border p-2 bg-white">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      </ScrollSync>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {['chatTogoVar', 'gpt4o', 'varChat'].map((section) => (
          <div key={section} className="border p-4 rounded space-y-2">
            <h3 className="font-bold text-lg">{section}</h3>
            {["Accuracy", "Completeness", "Logical Consistency", "Clarity and Conciseness", "Evidence Support"].map((field) => (
              <div key={field} className="space-y-1">
                <label>{field} Score (/10)</label>
                <Input
                  type="number"
                  min="0"
                  max="10"
                  value={form[section]?.[field]?.score || ''}
                  onChange={(e) => handleInputChange(section, field, 'score', e.target.value)}
                />
                <label>Reason (English)</label>
                <Input
                  value={form[section]?.[field]?.reason_en || ''}
                  onChange={(e) => handleInputChange(section, field, 'reason_en', e.target.value)}
                />
                <label>Reason (日本語)</label>
                <Input
                  value={form[section]?.[field]?.reason_ja || ''}
                  onChange={(e) => handleInputChange(section, field, 'reason_ja', e.target.value)}
                />
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="space-y-2">
        <Button onClick={handleUpload}>Upload Evaluation JSONL to GitHub</Button>
        {message && <p>{message}</p>}
      </div>
    </div>
  );
}
