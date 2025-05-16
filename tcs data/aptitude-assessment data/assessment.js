const fs = require("fs");
const readlineSync = require("readline-sync");

// Function to get random questions from topics
function getRandomQuestionsFromTopics(topics, totalNeeded) {
  let selected = [];
  
  for (let topic of topics) {
    const count = Math.random() < 0.5 ? 1 : 2;
    const shuffled = topic.questions.sort(() => 0.5 - Math.random());
    selected.push(...shuffled.slice(0, count));
  }

  if (selected.length > totalNeeded) {
    selected = selected.sort(() => 0.5 - Math.random()).slice(0, totalNeeded);
  } else if (selected.length < totalNeeded) {
    const all = topics.flatMap(t => t.questions);
    const extra = all
      .filter(q => !selected.some(s => s.id === q.id))
      .sort(() => 0.5 - Math.random())
      .slice(0, totalNeeded - selected.length);
    selected.push(...extra);
  }

  return selected;
}

// Load the JSON files
const quant = JSON.parse(fs.readFileSync("quant.json", "utf-8"));
const reasoning = JSON.parse(fs.readFileSync("reasoning.json", "utf-8"));
const verbal = JSON.parse(fs.readFileSync("verbal.json", "utf-8"));

// Skip cloze topic
const filteredVerbalTopics = verbal.topics.filter(topic => topic.name.toLowerCase() !== "cloze");

// Generate question sets for each section
const quantSet = getRandomQuestionsFromTopics(quant.topics, 20);
const reasoningSet = getRandomQuestionsFromTopics(reasoning.topics, 20);
const verbalSet = getRandomQuestionsFromTopics(filteredVerbalTopics, 25);

// Function to ask questions and get the result
function askQuestions(questions) {
  let correctCount = 0;
  questions.forEach((q, index) => {
    console.log(`\nQ${index + 1}: ${q.question}`);
    q.options.forEach((opt, idx) => {
      console.log(`   ${String.fromCharCode(65 + idx)}. ${opt}`);
    });

    const userAnswer = readlineSync.question("Your answer (A/B/C/D): ").toUpperCase();
    if (userAnswer === q.answer) {
      correctCount++;
    }
  });
  return correctCount;
}

// Ask questions and get results for each section
const quantScore = askQuestions(quantSet);
const verbalScore = askQuestions(verbalSet);
const reasoningScore = askQuestions(reasoningSet);

// Calculate the total score out of 65
const totalScore = quantScore + verbalScore + reasoningScore;

// Display the results
console.log("\n\n--- Results ---");
console.log(`Quantitative Reasoning Score: ${quantScore} / 20`);
console.log(`Verbal Ability Score: ${verbalScore} / 25`);
console.log(`Reasoning Ability Score: ${reasoningScore} / 20`);
console.log(`Total Score: ${totalScore} / 65`);
