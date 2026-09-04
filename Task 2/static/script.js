document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const input = document.getElementById('feedback-input');
    const modelSelect = document.getElementById('model-select');

    const resultContainer = document.getElementById('result-container');
    const spinnerBox = document.getElementById('spinner-box');
    const resultContent = document.getElementById('result-content');

    const sentimentOutput = document.getElementById('sentiment-output');
    const modelOutput = document.getElementById('model-output');

    analyzeBtn.addEventListener('click', async () => {
        const text = input.value.trim();
        if (!text) {
            alert('Please enter some feedback text to analyze.');
            return;
        }

        // Show UI Status
        resultContainer.classList.remove('hidden');
        spinnerBox.classList.remove('hidden');
        resultContent.classList.add('hidden');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    model: modelSelect.value
                })
            });

            const data = await response.json();

            const insightsContainer = document.getElementById('insights-container');
            const insightsTags = document.getElementById('insights-tags');

            if (response.ok) {
                sentimentOutput.textContent = data.sentiment;
                sentimentOutput.className = data.sentiment.toLowerCase(); // 'positive' or 'negative' css class
                modelOutput.textContent = `Analyzed by ${data.model}`;

                // Populate dynamic insights from the single predict endpoint
                if (data.insights && data.insights.length > 0) {
                    insightsTags.innerHTML = '';
                    data.insights.forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'insight-card';
                        card.innerHTML = `
                                <h4>${item.title}</h4>
                                <p>${item.desc}</p>
                                <div class="keyword-ref">Keyword Found: <span>${item.keyword}</span></div>
                            `;
                        insightsTags.appendChild(card);
                    });
                    insightsContainer.classList.remove('hidden');
                } else {
                    // Hide Insights pane if no relevant ones found for this prediction
                    insightsContainer.classList.add('hidden');
                }

            } else {
                sentimentOutput.textContent = 'Error';
                sentimentOutput.className = 'negative';
                modelOutput.textContent = data.error || 'Server error occurred.';
            }

        } catch (error) {
            sentimentOutput.textContent = 'Network Error';
            sentimentOutput.className = 'negative';
            modelOutput.textContent = 'Could not reach the analysis backend.';
        } finally {
            spinnerBox.classList.add('hidden');
            resultContent.classList.remove('hidden');
            analyzeBtn.disabled = false;
        }
    });

});
