'use client';

import { useState } from 'react';

interface ConservationFact {
  id: number;
  title: string;
  description: string;
  icon: string;
}

interface ActionStep {
  id: number;
  step: string;
  description: string;
  completed: boolean;
}

export default function FeatureExperience() {
  const [activeFact, setActiveFact] = useState<number>(0);
  const [actionSteps, setActionSteps] = useState<ActionStep[]>([
    { id: 1, step: '了解问题', description: '学习北极熊面临的威胁', completed: true },
    { id: 2, step: '减少碳足迹', description: '采取个人行动减少碳排放', completed: false },
    { id: 3, step: '支持保护组织', description: '捐款或成为志愿者', completed: false },
    { id: 4, step: '传播信息', description: '分享保护知识给更多人', completed: false },
  ]);

  const conservationFacts: ConservationFact[] = [
    {
      id: 1,
      title: '海冰的重要性',
      description: '北极熊依赖海冰进行狩猎、繁殖和迁徙。海冰的快速融化严重威胁它们的生存。',
      icon: '❄️'
    },
    {
      id: 2,
      title: '狩猎方式',
      description: '北极熊主要捕食海豹，它们会在海冰上等待海豹浮出水面呼吸时进行突袭。',
      icon: '🎣'
    },
    {
      id: 3,
      title: '繁殖周期',
      description: '雌性北极熊会在雪洞中冬眠并产仔，幼崽会跟随母亲学习生存技能长达2年。',
      icon: '👨‍👩‍👧‍👦'
    },
    {
      id: 4,
      title: '栖息地范围',
      description: '北极熊分布在北极圈内的五个国家：加拿大、俄罗斯、美国（阿拉斯加）、挪威和丹麦（格陵兰）。',
      icon: '🗺️'
    }
  ];

  const handleFactClick = (index: number) => {
    setActiveFact(index);
  };

  const toggleStepCompletion = (id: number) => {
    setActionSteps(prevSteps => 
      prevSteps.map(step => 
        step.id === id ? { ...step, completed: !step.completed } : step
      )
    );
  };

  const completedSteps = actionSteps.filter(step => step.completed).length;
  const progressPercentage = (completedSteps / actionSteps.length) * 100;

  return (
    <section className="feature-experience">
      <div className="container">
        <h2 className="section-title">互动体验</h2>
        
        <div className="experience-grid">
          {/* Conservation Facts Carousel */}
          <div className="facts-section">
            <h3 className="subsection-title">北极熊知识</h3>
            <div className="facts-carousel">
              <div className="facts-nav">
                {conservationFacts.map((fact, index) => (
                  <button
                    key={fact.id}
                    className={`fact-nav-button ${activeFact === index ? 'active' : ''}`}
                    onClick={() => handleFactClick(index)}
                    aria-label={`查看事实 ${index + 1}`}
                  >
                    {fact.icon}
                  </button>
                ))}
              </div>
              
              <div className="fact-display">
                <div className="fact-icon">{conservationFacts[activeFact].icon}</div>
                <h4 className="fact-title">{conservationFacts[activeFact].title}</h4>
                <p className="fact-description">{conservationFacts[activeFact].description}</p>
                <div className="fact-counter">
                  {activeFact + 1} / {conservationFacts.length}
                </div>
              </div>
            </div>
          </div>

          {/* Action Steps Tracker */}
          <div className="actions-section">
            <h3 className="subsection-title">你的保护行动</h3>
            
            <div className="progress-tracker">
              <div className="progress-header">
                <span className="progress-label">完成进度</span>
                <span className="progress-percentage">{Math.round(progressPercentage)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
              <div className="progress-stats">
                {completedSteps} / {actionSteps.length} 个步骤完成
              </div>
            </div>

            <div className="steps-list">
              {actionSteps.map(step => (
                <div 
                  key={step.id} 
                  className={`step-item ${step.completed ? 'completed' : ''}`}
                  onClick={() => toggleStepCompletion(step.id)}
                >
                  <div className="step-checkbox">
                    {step.completed ? '✓' : '○'}
                  </div>
                  <div className="step-content">
                    <h4 className="step-title">{step.step}</h4>
                    <p className="step-description">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="actions-encouragement">
              <p className="encouragement-text">
                {progressPercentage === 100 
                  ? '🎉 太棒了！你已经完成了所有保护行动！继续传播保护意识吧！'
                  : progressPercentage >= 50
                  ? '👍 做得好！继续努力完成剩下的行动步骤。'
                  : '💪 开始你的保护之旅吧！每一个小行动都能带来大改变。'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Impact Visualization */}
        <div className="impact-visualization">
          <h3 className="subsection-title">你的影响</h3>
          <div className="impact-grid">
            <div className="impact-item">
              <div className="impact-icon">🌍</div>
              <div className="impact-content">
                <h4 className="impact-title">减少碳排放</h4>
                <p className="impact-description">
                  通过节能和绿色出行，每年可减少约2吨二氧化碳排放。
                </p>
              </div>
            </div>
            <div className="impact-item">
              <div className="impact-icon">🐻</div>
              <div className="impact-content">
                <h4 className="impact-title">支持保护工作</h4>
                <p className="impact-description">
                  你的捐款可以帮助保护100平方米的北极熊栖息地。
                </p>
              </div>
            </div>
            <div className="impact-item">
              <div className="impact-icon">📢</div>
              <div className="impact-content">
                <h4 className="impact-title">传播影响力</h4>
                <p className="impact-description">
                  每分享一次，平均可以影响10个人关注北极熊保护。
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .feature-experience {
          padding: var(--spacing-xl) 0;
          background-color: var(--light-blue);
          border-radius: var(--radius-lg);
          margin: var(--spacing-xl) 0;
        }

        .experience-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: var(--spacing-lg);
          margin-bottom: var(--spacing-xl);
        }

        .subsection-title {
          color: var(--primary-blue);
          margin-bottom: var(--spacing-md);
          font-size: 1.5rem;
        }

        /* Facts Section */
        .facts-section {
          background: white;
          padding: var(--spacing-lg);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
        }

        .facts-carousel {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-md);
        }

        .facts-nav {
          display: flex;
          justify-content: center;
          gap: var(--spacing-sm);
          flex-wrap: wrap;
        }

        .fact-nav-button {
          background: var(--ice-blue);
          border: 2px solid transparent;
          border-radius: 50%;
          width: 50px;
          height: 50px;
          font-size: 1.5rem;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .fact-nav-button:hover {
          background: var(--accent-blue);
          color: white;
          transform: scale(1.1);
        }

        .fact-nav-button.active {
          background: var(--accent-blue);
          color: white;
          border-color: var(--primary-blue);
          transform: scale(1.1);
        }

        .fact-display {
          text-align: center;
          padding: var(--spacing-md);
        }

        .fact-icon {
          font-size: 4rem;
          margin-bottom: var(--spacing-md);
        }

        .fact-title {
          color: var(--primary-blue);
          margin-bottom: var(--spacing-sm);
          font-size: 1.3rem;
        }

        .fact-description {
          color: var(--text-dark);
          line-height: 1.6;
          margin-bottom: var(--spacing-md);
        }

        .fact-counter {
          color: var(--text-light);
          font-size: 0.9rem;
        }

        /* Actions Section */
        .actions-section {
          background: white;
          padding: var(--spacing-lg);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
        }

        .progress-tracker {
          background: var(--ice-blue);
          padding: var(--spacing-md);
          border-radius: var(--radius-md);
          margin-bottom: var(--spacing-lg);
        }

        .progress-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--spacing-sm);
        }

        .progress-label {
          font-weight: bold;
          color: var(--primary-blue);
        }

        .progress-percentage {
          font-weight: bold;
          color: var(--success-green);
          font-size: 1.2rem;
        }

        .progress-bar {
          height: 10px;
          background: rgba(0, 0, 0, 0.1);
          border-radius: 5px;
          overflow: hidden;
          margin-bottom: var(--spacing-sm);
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--success-green), var(--accent-blue));
          border-radius: 5px;
          transition: width 0.5s ease;
        }

        .progress-stats {
          text-align: center;
          color: var(--text-light);
          font-size: 0.9rem;
        }

        .steps-list {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-sm);
          margin-bottom: var(--spacing-lg);
        }

        .step-item {
          display: flex;
          align-items: flex-start;
          gap: var(--spacing-sm);
          padding: var(--spacing-sm);
          border-radius: var(--radius-sm);
          cursor: pointer;
          transition: background-color 0.3s ease;
        }

        .step-item:hover {
          background-color: var(--ice-blue);
        }

        .step-item.completed {
          opacity: 0.7;
        }

        .step-checkbox {
          width: 24px;
          height: 24px;
          border: 2px solid var(--accent-blue);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.8rem;
          color: var(--accent-blue);
          flex-shrink: 0;
        }

        .step-item.completed .step-checkbox {
          background-color: var(--success-green);
          border-color: var(--success-green);
          color: white;
        }

        .step-content {
          flex: 1;
        }

        .step-title {
          color: var(--primary-blue);
          font-size: 1rem;
          margin-bottom: 2px;
        }

        .step-description {
          color: var(--text-light);
          font-size: 0.9rem;
        }

        .actions-encouragement {
          text-align: center;
          padding: var(--spacing-md);
          background: linear-gradient(135deg, var(--light-blue), var(--ice-blue));
          border-radius: var(--radius-md);
        }

        .encouragement-text {
          color: var(--primary-blue);
          font-weight: 500;
          margin: 0;
        }

        /* Impact Visualization */
        .impact-visualization {
          background: white;
          padding: var(--spacing-lg);
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-md);
        }

        .impact-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: var(--spacing-md);
        }

        .impact-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-md);
          padding: var(--spacing-md);
          background: var(--ice-blue);
          border-radius: var(--radius-md);
        }

        .impact-icon {
          font-size: 2.5rem;
          flex-shrink: 0;
        }

        .impact-content {
          flex: 1;
        }

        .impact-title {
          color: var(--primary-blue);
          font-size: 1.1rem;
          margin-bottom: 4px;
        }

        .impact-description {
          color: var(--text-dark);
          font-size: 0.9rem;
          line-height: 1.5;
        }

        /* Responsive Design */
        @media (min-width: 768px) {
          .experience-grid {
            grid-template-columns: 1fr 1fr;
          }

          .impact-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        @media (min-width: 1024px) {
          .facts-carousel {
            flex-direction: row;
            align-items: center;
          }

          .facts-nav {
            flex-direction: column;
            gap: var(--spacing-sm);
          }

          .fact-display {
            flex: 1;
            text-align: left;
          }
        }
      `}</style>
    </section>
  );
}