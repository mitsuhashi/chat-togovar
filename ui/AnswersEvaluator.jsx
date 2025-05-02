import React, { useState, useEffect, useRef } from 'react';
import { Octokit } from '@octokit/rest';
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

export default function AnswersEvaluator() {
  const [token, setToken] = useState('');
  const [filePairs, setFilePairs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [fileContents, setFileContents] = useState(['', '', '']);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ ChatTogoVar: {}, GPT4o: {}, VarChat: {} });
  const [questionText, setQuestionText] = useState('');
  const [questionJa, setQuestionJa] = useState('');

  const scrollRefs = {
    ChatTogoVar: useRef(null),
    GPT4o: useRef(null),
    VarChat: useRef(null),
  };

  const octokit = new Octokit({ auth: token });

  const handleScroll = (sourceKey) => (e) => {
    const scrollTop = e.target.scrollTop;
    Object.keys(scrollRefs).forEach((key) => {
      if (key !== sourceKey && scrollRefs[key].current) {
        scrollRefs[key].current.scrollTop = scrollTop;
      }
    });
  };

  useEffect(() => {
    const storedToken = localStorage.getItem('gh_token');
    if (storedToken) setToken(storedToken);
  }, []);

  useEffect(() => {
    if (token) localStorage.setItem('gh_token', token);
  }, [token]);

  useEffect(() => {
    if (filePairs.length > 0 && currentIndex < filePairs.length) {
      setMessage('');
      fetchFiles(filePairs[currentIndex]);
    }
  }, [currentIndex, filePairs]);

  const fetchFilePairs = async () => {
    try {
      const { data } = await octokit.repos.getContent({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path: 'evaluation/human/sampled_150.json'
      });
      const content = base64ToUtf8(data.content);
      const samples = JSON.parse(content);
      const pairs = samples.map(({ QuestionNumber, rsid }) => ({ qY: QuestionNumber, rsXXXX: `${rsid}.md` }));
      setFilePairs(pairs);
      setMessage(`✅ Sampled pairs loaded: ${pairs.length}件`);
    } catch (err) {
      setMessage(`❌ Failed to load sampled_150.json: ${err.message}`);
    }
  };

  const fetchQuestion = async (qY, rs) => {
    const en = await octokit.request('GET /repos/mitsuhashi/chat-togovar/contents/questions.json');
    const questionsEn = JSON5.parse(base64ToUtf8(en.data.content));
    setQuestionText(questionsEn[qY]?.replace('{rs}', rs) || 'Question template not found');
    try {
      const ja = await octokit.request('GET /repos/mitsuhashi/chat-togovar/contents/questions_ja.json');
      const questionsJa = JSON5.parse(base64ToUtf8(ja.data.content));
      setQuestionJa(questionsJa[qY]?.replace('{rs}', rs) || '質問テンプレートが見つかりません');
    } catch {
      setQuestionJa('和訳データの読み込みに失敗しました');
    }
  };

  const fetchFiles = async (pair) => {
    setFileContents(['', '', '']);

    const rs = pair.rsXXXX.replace('.md', '');
    await fetchQuestion(pair.qY, rs);

    const paths = [
      `answers/chat_togovar/${pair.qY}/${pair.rsXXXX}`,
      `answers/gpt-4o/${pair.qY}/${pair.rsXXXX}`,
      `answers/varchat/${pair.rsXXXX}`
    ];

    const contents = await Promise.all(paths.map(async (path) => {
      try {
        const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
        return base64ToUtf8(data.content);
      } catch {
        return '(Content unavailable)';
      }
    }));
    setFileContents(contents);

    const path = `evaluation/human/evaluation_${currentIndex}_${pair.qY}_${rs}.json`;
    try {
      const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
      const record = JSON.parse(base64ToUtf8(data.content));
      if (record?.evaluation) {
        setForm(record.evaluation);
        setMessage('✅ 評価フォームがリストアされました');
      }
    } catch {
      setForm({ ChatTogoVar: {}, GPT4o: {}, VarChat: {} });
    }
  };

  const handleInputChange = (model, field, subfield, value) => {
    setForm((prev) => ({
      ...prev,
      [model]: {
        ...prev[model],
        [field]: {
          ...prev[model]?.[field],
          [subfield]: value
        }
      }
    }));
  };

  const handleUpload = async () => {
    if (!filePairs[currentIndex]) {
      setMessage('❌ ファイルペアが存在しません');
      return;
    }
    const pair = filePairs[currentIndex];
    const rs = pair.rsXXXX?.replace('.md', '');
    if (!rs || !pair.qY) {
      setMessage('❌ 必要なファイル情報が不正です');
      return;
    }
    const path = `evaluation/human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.json`;
    let sha;
    try {
      const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
      sha = data.sha;
    } catch (err) {
      if (err.status !== 404) throw err;
    }
    const jsonContent = JSON.stringify({
      ...filePairs[currentIndex],
      evaluation: form
    }, null, 2);
    const base64Content = utf8ToBase64(jsonContent);

    try {
      await octokit.repos.createOrUpdateFileContents({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path,
        message: `Add human evaluation result for ${rs}`,
        content: base64Content,
        sha
      });
      setMessage('✅ Uploaded to GitHub!');
    } catch (error) {
      setMessage(`❌ Upload failed: ${error.message}`);
    }
  };

  const handleDelete = async () => {
    const rs = filePairs[currentIndex].rsXXXX.replace('.md', '');
    const path = `evaluation/human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.json`;
    try {
      const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
      await octokit.repos.deleteFile({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path,
        message: `Delete human evaluation for ${rs}`,
        sha: data.sha
      });
      setForm({ ChatTogoVar: {}, GPT4o: {}, VarChat: {} });
      setMessage('🗑️ Deleted evaluation file');
    } catch (error) {
      setMessage(`❌ Delete failed: ${error.message}`);
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

      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
        <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${((currentIndex + 1) / filePairs.length) * 100}%` }}></div>
      </div>
      <p className="text-sm text-gray-500">{currentIndex + 1} / {filePairs.length} 問</p>

      <div className="space-y-2">
        <Button onClick={handleUpload}>Upload Evaluation JSON to GitHub</Button>
        <Button variant="destructive" onClick={handleDelete}>Delete Evaluation JSON</Button>
        {message && <div className="text-green-600 font-medium mt-2">{message}</div>}
      </div>

      <div className="border p-4 bg-gray-50 rounded">
        <h2 className="font-bold">Question</h2>
        <p className="mb-1">{questionText}</p>
        <p className="text-gray-700 italic">{questionJa}</p>
      </div>

      <div className="space-y-6">
        {["ChatTogoVar", "GPT4o", "VarChat"].map((model, idx) => (
          <div key={model} className="border rounded-xl shadow p-4 bg-white flex flex-col md:flex-row gap-6">
            <div className="w-full md:w-2/3 h-[40vh] overflow-auto" ref={scrollRefs[model]} onScroll={handleScroll(model)}>
              <h4 className="font-semibold text-lg mb-2">Answer: {model}</h4>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{fileContents[idx]}</ReactMarkdown>
              </div>
            </div>
            <div className="w-full md:w-1/3 space-y-3">
              {["Accuracy", "Completeness", "Logical Consistency", "Clarity and Conciseness", "Evidence Support"].map((field) => (
                <div key={field} className="space-y-1">
                  <label className="block font-medium text-sm">{field} Score</label>
                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: 11 }, (_, i) => (
                      <label key={i} className="flex items-center space-x-1 text-xs">
                        <input
                          type="radio"
                          name={`${model}-${field}`}
                          value={i}
                          checked={form[model]?.[field]?.score === String(i)}
                          onChange={(e) => handleInputChange(model, field, 'score', e.target.value)}
                        />
                        <span>{i}</span>
                      </label>
                    ))}
                  </div>
                  <textarea
                    placeholder="Reason (English)"
                    className="w-full border rounded p-2 resize-x"
                    rows={3}
                    value={form[model]?.[field]?.reason_en || ''}
                    onChange={(e) => handleInputChange(model, field, 'reason_en', e.target.value)}
                  />
                  <textarea
                    placeholder="Reason (日本語)"
                    className="w-full border rounded p-2 resize-x"
                    rows={3}
                    value={form[model]?.[field]?.reason_ja || ''}
                    onChange={(e) => handleInputChange(model, field, 'reason_ja', e.target.value)}
                  />
                </div>
              ))}
              <p className="text-sm font-semibold pt-1">
                Total Score: {
                  Object.values(form[model] || {}).reduce((acc, val) => acc + (parseInt(val.score || 0, 10)), 0)
                } / 50
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}