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
  const [questionJa, setQuestionJa] = useState('');
  const [sampleIndex, setSampleIndex] = useState(null);

  const scrollRefs = {
    A: useRef(null),
    B: useRef(null),
    C: useRef(null),
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
    const saved = localStorage.getItem(`eval_${currentIndex}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setForm(parsed);
      } catch {}
    }
  }, [currentIndex]);

  useEffect(() => {
    localStorage.setItem(`eval_${currentIndex}`, JSON.stringify(form));
  }, [form, currentIndex]);

  useEffect(() => {
    if (filePairs.length > 0 && currentIndex < filePairs.length) {
      setMessage(''); // ページ遷移時にメッセージをクリア
      fetchFiles(filePairs[currentIndex]);
    }
  }, [currentIndex, filePairs]);


  const fetchFilePairs = async () => {
    try {
      const { data } = await octokit.repos.getContent({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path: 'evaluation/human/sampled_30_each.json'
      });
      const content = base64ToUtf8(data.content);
      const samples = JSON.parse(content);
      const pairs = samples.map(({ QuestionNumber, rsid }) => ({ qY: QuestionNumber, rsXXXX: `${rsid}.md` }));
      setFilePairs(pairs);
      setMessage(`✅ Sampled pairs loaded: ${pairs.length}件`);
      console.log('Loaded pairs:', pairs);
    } catch (err) {
      setMessage(`❌ Failed to load sampled_30_each.json: ${err.message}`);
      console.error('Error loading sampled_30_each.json', err);
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
    setShuffledLabels([]);
    setFileContents(['', '', '']);

    const rs = pair.rsXXXX.replace('.md', '');
    await fetchQuestion(pair.qY, rs);

    const paths = [
      { label: 'ChatTogoVar', path: `answers/chat_togovar/${pair.qY}/${pair.rsXXXX}` },
      { label: 'GPT-4o', path: `answers/gpt-4o/${pair.qY}/${pair.rsXXXX}` },
      { label: 'VarChat', path: `answers/varchat/${pair.rsXXXX}` }
    ];

    const shuffled = shuffle(['A', 'B', 'C'].map((k, i) => ({ key: k, label: paths[i].label, path: paths[i].path })));
    setShuffledLabels(shuffled);

    const contents = await Promise.all(shuffled.map(async (item) => {
      try {
        const { data } = await octokit.repos.getContent({
          owner: 'mitsuhashi',
          repo: 'chat-togovar',
          path: item.path
        });
        return base64ToUtf8(data.content);
      } catch {
        return '(Content unavailable)';
      }
    }));
    setFileContents(contents);

    const path = `evaluation/human/evaluation_${currentIndex}_${filePairs[currentIndex]?.qY}_${rs}.jsonl`;
    try {
      const { data } = await octokit.repos.getContent({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path
      });
      const record = JSON.parse(base64ToUtf8(data.content));
      if (record?.evaluation) {
        setForm(record.evaluation);
        setMessage('✅ 評価フォームがリストアされました');
      }
    } catch {}
  };

  const handleInputChange = (key, field, subfield, value) => {
    setForm((prev) => ({
      ...prev,
      [key]: {
        ...prev[key],
        [field]: {
          ...prev[key]?.[field],
          [subfield]: value
        }
      }
    }));
  };

  const handleUpload = async () => {
    const rs = filePairs[currentIndex].rsXXXX.replace('.md', '');
    const path = `evaluation/human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.jsonl`;
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
        message: `Add human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.jsonl`,
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
    const path = `evaluation/human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.jsonl`;
    try {
      const { data } = await octokit.repos.getContent({ owner: 'mitsuhashi', repo: 'chat-togovar', path });
      await octokit.repos.deleteFile({
        owner: 'mitsuhashi',
        repo: 'chat-togovar',
        path,
        message: `Delete human/evaluation_${currentIndex}_${filePairs[currentIndex].qY}_${rs}.jsonl`,
        sha: data.sha
      });
      setMessage('🗑️ Deleted evaluation file');
      setForm({ A: {}, B: {}, C: {} });
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
        <Button onClick={handleUpload}>Upload Evaluation JSONL to GitHub</Button>
        <Button variant="destructive" onClick={handleDelete}>Delete Evaluation JSONL</Button>
        {message && <div className="text-green-600 font-medium mt-2">{message}</div>}
      </div>

      <div className="border p-4 bg-gray-50 rounded">
        <h2 className="font-bold">Question</h2>
        <p><span className="text-sm text-gray-500">Index: {currentIndex + 1}</span></p>
        <p className="mb-1">{questionText}</p>
        <p className="text-gray-700 italic">{questionJa}</p>
      </div>

      <div className="space-y-6">
        {['A', 'B', 'C'].map((key, idx) => (
          <div key={key} className="border rounded-xl shadow p-4 bg-white flex flex-col md:flex-row gap-6">
            <div className="w-full md:w-2/3 h-[40vh] overflow-auto" ref={scrollRefs[key]} onScroll={handleScroll(key)}>
              <h4 className="font-semibold text-lg mb-2">Answer {key}</h4>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{fileContents[idx]}</ReactMarkdown>
              </div>
            </div>
            <div className="w-full md:w-1/3 space-y-3">
              {['Accuracy', 'Completeness', 'Logical Consistency', 'Clarity and Conciseness', 'Evidence Support'].map((field) => (
                <div key={field} className="space-y-1">
                  <label className="block font-medium text-sm">{field} Score</label>
                  <div className="flex flex-wrap gap-1">
                    {Array.from({ length: 11 }, (_, i) => (
                      <label key={i} className="flex items-center space-x-1 text-xs">
                        <input
                          type="radio"
                          name={`${key}-${field}`}
                          value={i}
                          checked={form[key]?.[field]?.score === String(i)}
                          onChange={(e) => handleInputChange(key, field, 'score', e.target.value)}
                        />
                        <span>{i}</span>
                      </label>
                    ))}
                  </div>
                  <textarea
                    placeholder="Reason (English)"
                    className="w-full border rounded p-2 resize-x"
                    rows={3}
                    value={form[key]?.[field]?.reason_en || ''}
                    onChange={(e) => handleInputChange(key, field, 'reason_en', e.target.value)}
                  />
                  <textarea
                    placeholder="Reason (日本語)"
                    className="w-full border rounded p-2 resize-x"
                    rows={3}
                    value={form[key]?.[field]?.reason_ja || ''}
                    onChange={(e) => handleInputChange(key, field, 'reason_ja', e.target.value)}
                  />
                </div>
              ))}
              <p className="text-sm font-semibold pt-1">
                Total Score: {
                  Object.values(form[key] || {}).reduce((acc, val) => acc + (parseInt(val.score || 0, 10)), 0)
                } / 50
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        <Button onClick={handleUpload}>Upload Evaluation JSONL to GitHub</Button>
        <Button variant="destructive" onClick={handleDelete}>Delete Evaluation JSONL</Button>
        {message && <div className="text-green-600 font-medium mt-2">{message}</div>}
      </div>
    </div>
  );
}