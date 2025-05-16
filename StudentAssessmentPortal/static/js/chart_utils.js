// Utility functions for charts

/**
 * Creates a radar chart for topic performance visualization
 * @param {string} containerId - ID of the container element
 * @param {Array} topics - Array of topic data objects
 * @param {string} title - Chart title
 */
function createTopicRadarChart(containerId, topics, title) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Check if data exists
    if (!topics || topics.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No topic data available.</div>';
        return;
    }
    
    // Prepare chart data
    const labels = topics.map(topic => topic.topic);
    const data = topics.map(topic => topic.percentage);
    
    // Create canvas element
    container.innerHTML = '<canvas></canvas>';
    const ctx = container.querySelector('canvas').getContext('2d');
    
    // Create chart
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Topic Performance (%)',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
                }
            },
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#666',
                        backdropColor: 'transparent',
                        z: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                        color: '#666'
                    }
                }
            }
        }
    });
}

/**
 * Creates a doughnut chart for overall score visualization
 * @param {string} containerId - ID of the container element
 * @param {number} score - Current score
 * @param {number} maxScore - Maximum possible score
 * @param {string} title - Chart title
 * @param {string} colorClass - CSS color class for the chart
 */
function createScoreDoughnutChart(containerId, score, maxScore, title, colorClass) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Determine colors based on colorClass
    let borderColor, backgroundColor;
    
    switch (colorClass) {
        case 'success':
            borderColor = 'rgba(40, 167, 69, 1)';
            backgroundColor = 'rgba(40, 167, 69, 0.2)';
            break;
        case 'warning':
            borderColor = 'rgba(255, 193, 7, 1)';
            backgroundColor = 'rgba(255, 193, 7, 0.2)';
            break;
        case 'danger':
            borderColor = 'rgba(220, 53, 69, 1)';
            backgroundColor = 'rgba(220, 53, 69, 0.2)';
            break;
        case 'info':
        default:
            borderColor = 'rgba(23, 162, 184, 1)';
            backgroundColor = 'rgba(23, 162, 184, 0.2)';
    }
    
    // Create canvas element
    container.innerHTML = '<canvas></canvas>';
    const ctx = container.querySelector('canvas').getContext('2d');
    
    // Calculate percentage
    const percentage = Math.round((score / maxScore) * 100);
    
    // Create chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Score', 'Remaining'],
            datasets: [{
                data: [score, maxScore - score],
                backgroundColor: [borderColor, 'rgba(150, 150, 150, 0.2)'],
                borderColor: [borderColor, 'rgba(150, 150, 150, 0.5)'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                title: {
                    display: true,
                    text: title,
                    color: '#333'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.dataIndex === 0) {
                                return `Score: ${score}/${maxScore} (${percentage}%)`;
                            } else {
                                return `Remaining: ${maxScore - score}`;
                            }
                        }
                    }
                }
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                const width = chart.width;
                const height = chart.height;
                const ctx = chart.ctx;
                
                ctx.restore();
                ctx.font = '1.5rem sans-serif';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = '#333';
                
                const text = `${percentage}%`;
                const textX = Math.round((width - ctx.measureText(text).width) / 2);
                const textY = height / 2;
                
                ctx.fillText(text, textX, textY);
                ctx.save();
            }
        }]
    });
}