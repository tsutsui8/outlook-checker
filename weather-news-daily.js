/**
 * 石和温泉 旅館フロント 毎日ブリーフィング自動送信スクリプト
 *
 * 機能:
 *   - 笛吹市（石和町）の天気予報を取得（Open-Meteo API / 無料・APIキー不要）
 *   - 国内ニュース3件（NHK RSS）+ 海外ニュース2件（BBC日本語 RSS）を取得
 *   - Claude AI が旅館フロント視点の解説付きメールを生成
 *   - Gmail へ自動送信（Nodemailer + Gmailアプリパスワード）
 *
 * セットアップ:
 *   1. .env ファイルを編集して GMAIL_APP_PASSWORD と ANTHROPIC_API_KEY を設定
 *   2. npm install を実行
 *   3. node weather-news-daily.js でテスト実行
 *   4. Windowsタスクスケジューラで run-daily-briefing.bat を毎朝登録
 */

require('dotenv').config();
const axios = require('axios');
const Parser = require('rss-parser');
const nodemailer = require('nodemailer');
const Anthropic = require('@anthropic-ai/sdk');

// ─────────────────────────────────────────────
// WMO 天気コード → 日本語
// ─────────────────────────────────────────────
const WMO = {
  0: '快晴', 1: '概ね晴れ', 2: '晴れ時々曇り', 3: '曇り',
  45: '霧', 48: '霧（着氷）',
  51: '霧雨（弱）', 53: '霧雨', 55: '霧雨（強）',
  61: '小雨', 63: '雨', 65: '大雨',
  71: '小雪', 73: '雪', 75: '大雪', 77: 'あられ',
  80: 'にわか雨（弱）', 81: 'にわか雨', 82: 'にわか雨（強）',
  85: 'にわか雪', 86: 'にわか雪（強）',
  95: '雷雨', 96: '雷雨（ひょう）', 99: '雷雨（激しいひょう）',
};
const wmo = (code) => WMO[code] ?? `天気コード ${code}`;

// ─────────────────────────────────────────────
// 日付フォーマット
// ─────────────────────────────────────────────
function formatDate(isoDate) {
  return new Date(isoDate).toLocaleDateString('ja-JP', {
    month: 'long', day: 'numeric', weekday: 'short',
    timeZone: 'Asia/Tokyo',
  });
}

function todayJa() {
  return new Date().toLocaleDateString('ja-JP', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
    timeZone: 'Asia/Tokyo',
  });
}

// ─────────────────────────────────────────────
// 天気取得 (Open-Meteo API)
// 笛吹市石和町の座標: 35.698, 138.716
// ─────────────────────────────────────────────
async function getWeather() {
  const { data } = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: {
      latitude: 35.698,
      longitude: 138.716,
      daily: [
        'weather_code',
        'temperature_2m_max',
        'temperature_2m_min',
        'precipitation_probability_max',
        'wind_speed_10m_max',
        'uv_index_max',
      ].join(','),
      wind_speed_unit: 'ms',
      timezone: 'Asia/Tokyo',
      forecast_days: 3,
    },
  });

  const d = data.daily;
  return [0, 1, 2].map((i) => ({
    date: formatDate(d.time[i]),
    weather: wmo(d.weather_code[i]),
    tempMax: d.temperature_2m_max[i],
    tempMin: d.temperature_2m_min[i],
    precipProb: d.precipitation_probability_max[i],
    windMax: d.wind_speed_10m_max[i],
    uvIndex: d.uv_index_max[i],
  }));
}

// ─────────────────────────────────────────────
// ニュース取得 (RSS)
// ─────────────────────────────────────────────
async function getNews() {
  const parser = new Parser({ timeout: 10000 });

  const [nhkRes, bbcRes] = await Promise.allSettled([
    parser.parseURL('https://www3.nhk.or.jp/rss/news/cat0.xml'),
    parser.parseURL('https://feeds.bbci.co.uk/japanese/rss.xml'),
  ]);

  const domestic = nhkRes.status === 'fulfilled'
    ? nhkRes.value.items.slice(0, 3).map((item) => item.title)
    : ['NHK RSSの取得に失敗しました'];

  const international = bbcRes.status === 'fulfilled'
    ? bbcRes.value.items.slice(0, 2).map((item) => item.title)
    : ['BBC日本語 RSSの取得に失敗しました'];

  return { domestic, international };
}

// ─────────────────────────────────────────────
// Claude API でブリーフィング生成
// ─────────────────────────────────────────────
async function generateBriefing(forecasts, news, dateStr) {
  const client = new Anthropic();

  const weatherBlock = forecasts.map((f, i) => {
    const label = ['【今日】', '【明日】', '【明後日】'][i];
    return `${label} ${f.date}
  天気: ${f.weather}　最高: ${f.tempMax}℃ / 最低: ${f.tempMin}℃
  降水確率: ${f.precipProb}%　最大風速: ${f.windMax}m/s　UV指数: ${f.uvIndex}`;
  }).join('\n\n');

  const newsBlock = [
    '≪国内ニュース（NHK）≫',
    ...news.domestic.map((t, i) => `${i + 1}. ${t}`),
    '',
    '≪海外ニュース（BBC日本語）≫',
    ...news.international.map((t, i) => `${i + 1}. ${t}`),
  ].join('\n');

  const prompt = `あなたは山梨県笛吹市石和温泉にある老舗旅館のベテランフロントマンです。
今日は${dateStr}です。

以下の天気情報とニュースをもとに、朝のフロントスタッフ向けブリーフィングメールを日本語で作成してください。

━━━ 天気情報 ━━━
${weatherBlock}

━━━ 最新ニュース ━━━
${newsBlock}

━━━ 作成ルール ━━━
1. 件名を最初の行に「件名：」で始めること
2. 天気セクションでは以下を必ず含めること
   - 今日・明日・明後日の天気サマリー
   - 旅館運営上の注意点（傘の貸し出し、送迎タイミング、館内温度管理、布団の調整など）
   - お客様との会話ネタになる天気の話題
3. ニュースセクションでは各ニュースに以下を添えること
   - 石和温泉の旅館フロントとして知っておくべき理由（訪日客への影響・経済動向・安全情報など）
   - 必要に応じてお客様への案内フレーズ例
4. 締めくくりに今日の接客テーマを一言で
5. 読みやすく、実務的なトーンで記述すること`;

  const message = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 2500,
    messages: [{ role: 'user', content: prompt }],
  });

  return message.content[0].text;
}

// ─────────────────────────────────────────────
// Gmail 送信
// ─────────────────────────────────────────────
async function sendEmail(subject, body) {
  const user = process.env.GMAIL_USER;
  const pass = process.env.GMAIL_APP_PASSWORD;

  if (!user || !pass) {
    throw new Error('.env に GMAIL_USER と GMAIL_APP_PASSWORD を設定してください');
  }

  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user, pass },
  });

  await transporter.sendMail({
    from: `石和温泉フロントブリーフィング <${user}>`,
    to: user,
    subject,
    text: body,
  });
}

// ─────────────────────────────────────────────
// メイン
// ─────────────────────────────────────────────
async function main() {
  const dateStr = todayJa();
  console.log(`[${dateStr}] ブリーフィング生成開始...`);

  // 天気・ニュースを並列取得
  const [forecasts, news] = await Promise.all([getWeather(), getNews()]);
  console.log('✓ 天気・ニュース取得完了');

  // Claude でメール本文を生成
  const briefing = await generateBriefing(forecasts, news, dateStr);
  console.log('✓ ブリーフィング生成完了');

  // 件名を1行目から抽出
  const lines = briefing.split('\n').filter((l) => l.trim() !== '');
  let subject = `【石和温泉フロントブリーフィング】${dateStr}`;
  let body = briefing;

  const subjectLine = lines.find((l) => l.startsWith('件名：') || l.startsWith('件名:'));
  if (subjectLine) {
    subject = subjectLine.replace(/^件名[：:]\s*/, '').trim();
    body = briefing.replace(subjectLine, '').trim();
  }

  // 送信
  await sendEmail(subject, body);
  console.log(`✓ メール送信完了: ${subject}`);
}

main().catch((err) => {
  console.error('✗ エラー:', err.message);
  process.exit(1);
});
