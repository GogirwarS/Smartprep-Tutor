document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs
    const tabTriggers = document.querySelectorAll('[data-bs-toggle="tab"]');
    tabTriggers.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('href');
            if (targetId === '#progress-tab') {
                // Refresh charts when progress tab is shown
                refreshProgressCharts();
            }
        });
    });
    
    // Fetch assessment data and initialize dashboard
    fetchAssessmentData()
        .then(data => {
            renderTopicPerformance(data.topics);
            setupProgressCharts(data.history);
        })
        .catch(error => {
            console.error('Failed to load assessment data:', error);
            document.getElementById('loading-indicator').innerHTML = 
                '<div class="alert alert-danger">Failed to load your assessment data. Please refresh the page.</div>';
        });
    
    // Fetch assessment data from the server
    async function fetchAssessmentData() {
        const response = await fetch('/api/get-assessment-data');
        if (!response.ok) {
            throw new Error('Failed to fetch assessment data');
        }
        return await response.json();
    }
    
    // Render topic performance sections
    function renderTopicPerformance(topicsData) {
        renderCategoryTopics('quant-topics', topicsData.quant);
        renderCategoryTopics('verbal-topics', topicsData.verbal);
        renderCategoryTopics('reasoning-topics', topicsData.reasoning);
        
        // Hide loading indicator
        document.getElementById('loading-indicator').classList.add('d-none');
        
        // Show content
        document.getElementById('dashboard-content').classList.remove('d-none');
    }
    
    // Render topics for a specific category
    function renderCategoryTopics(containerId, topics) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Sort topics by performance (worst to best)
        const sortedTopics = [...topics].sort((a, b) => a.percentage - b.percentage);
        
        let html = '';
        
        if (sortedTopics.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No assessment data available for this category yet.</div>';
            return;
        }
        
        // Create strength and weakness sections
        const weakTopics = sortedTopics.filter(t => t.percentage < 40);
        const mediumTopics = sortedTopics.filter(t => t.percentage >= 40 && t.percentage < 70);
        const strongTopics = sortedTopics.filter(t => t.percentage >= 70);
        
        // Weak topics section
        if (weakTopics.length > 0) {
            html += '<h5 class="text-danger">Needs Improvement</h5>';
            html += '<div class="mb-4">';
            weakTopics.forEach(topic => {
                html += createTopicProgressBar(topic, 'bg-danger');
            });
            html += '</div>';
        }
        
        // Medium topics section
        if (mediumTopics.length > 0) {
            html += '<h5 class="text-warning">Getting Better</h5>';
            html += '<div class="mb-4">';
            mediumTopics.forEach(topic => {
                html += createTopicProgressBar(topic, 'bg-warning');
            });
            html += '</div>';
        }
        
        // Strong topics section
        if (strongTopics.length > 0) {
            html += '<h5 class="text-success">Strengths</h5>';
            html += '<div class="mb-4">';
            strongTopics.forEach(topic => {
                html += createTopicProgressBar(topic, 'bg-success');
            });
            html += '</div>';
        }
        
        container.innerHTML = html;
    }
    
    // Create a progress bar for a topic
    function createTopicProgressBar(topic, colorClass) {
        return `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span>${topic.topic}</span>
                    <span class="badge ${colorClass}">${topic.correct}/${topic.total} (${topic.percentage}%)</span>
                </div>
                <div class="progress">
                    <div class="progress-bar ${colorClass}" role="progressbar" style="width: ${topic.percentage}%" 
                         aria-valuenow="${topic.percentage}" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>
        `;
    }
    
    // Setup progress charts
    function setupProgressCharts(historyData) {
        // Initialize chart containers
        createProgressChart('quant-progress', historyData.quant, 'Quantitative Progress', 20);
        createProgressChart('verbal-progress', historyData.verbal, 'Verbal Progress', 25);
        createProgressChart('reasoning-progress', historyData.reasoning, 'Reasoning Progress', 20);
        createOverallProgressChart('overall-progress', historyData);
    }
    
    // Create a progress chart for a specific category
    function createProgressChart(containerId, data, title, maxScore) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Check if data exists
        if (data.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No historical data available yet.</div>';
            return;
        }
        
        // Prepare chart data
        const dates = data.map(item => item.date);
        const scores = data.map(item => item.score);
        const percentages = data.map(item => Math.round((item.score / item.max_score) * 100));
        
        // Create canvas for the chart
        container.innerHTML = '<canvas></canvas>';
        const ctx = container.querySelector('canvas').getContext('2d');
        
        // Create chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Score',
                    data: scores,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        color: '#333'
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: '#333'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Score: ${context.raw}/${maxScore} (${percentages[context.dataIndex]}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#666'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        min: 0,
                        max: maxScore,
                        ticks: {
                            color: '#666'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    // Create an overall progress chart combining all categories
    function createOverallProgressChart(containerId, historyData) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        // Combine all dates
        const allDates = new Set();
        Object.values(historyData).forEach(categoryData => {
            categoryData.forEach(item => allDates.add(item.date));
        });
        
        // Convert to array and sort
        const sortedDates = Array.from(allDates).sort();
        
        // Check if any data exists
        if (sortedDates.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No historical data available yet.</div>';
            return;
        }
        
        // Create datasets
        const datasets = [
            {
                label: 'Quantitative',
                data: createDataPointsForDates(sortedDates, historyData.quant, 20),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                borderWidth: 2,
                fill: false
            },
            {
                label: 'Verbal',
                data: createDataPointsForDates(sortedDates, historyData.verbal, 25),
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.5)',
                borderWidth: 2,
                fill: false
            },
            {
                label: 'Reasoning',
                data: createDataPointsForDates(sortedDates, historyData.reasoning, 20),
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
                borderWidth: 2,
                fill: false
            }
        ];
        
        // Create canvas for the chart
        container.innerHTML = '<canvas></canvas>';
        const ctx = container.querySelector('canvas').getContext('2d');
        
        // Create chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedDates,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Overall Progress',
                        color: '#333'
                    },
                    legend: {
                        display: true,
                        labels: {
                            color: '#333'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#666'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: {
                            color: '#666',
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    // Create data points for chart based on dates
    function createDataPointsForDates(dates, categoryData, maxScore) {
        return dates.map(date => {
            const dataPoint = categoryData.find(item => item.date === date);
            if (dataPoint) {
                return Math.round((dataPoint.score / dataPoint.max_score) * 100);
            }
            return null; // Use null for missing data points
        });
    }
    
    // Refresh progress charts
    function refreshProgressCharts() {
        // This function will be called when switching to the progress tab
        // If charts are already initialized, they will resize properly
        if (typeof window.dispatchEvent === 'function') {
            window.dispatchEvent(new Event('resize'));
        }
    }
});