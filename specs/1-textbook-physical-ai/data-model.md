# Data Model: Physical AI & Humanoid Robotics Textbook

## Entity: Textbook Chapter
- **Fields**:
  - chapterId: unique identifier
  - title: string
  - content: markdown text
  - learningOutcomes: array of learning outcome statements
  - prerequisites: array of chapter IDs
  - targetAudience: beginner/intermediate
  - estimatedTime: number (hours)
  - difficultyLevel: 1-5 scale
  - associatedResources: array of resource IDs
  - experimentGuides: array of experiment guide IDs
  - knowledgeChecks: array of assessment questions
  - safetyRules: array of safety rule IDs

## Entity: Learning Outcome
- **Fields**:
  - outcomeId: unique identifier
  - description: measurable statement of what student should understand/do
  - chapterId: associated chapter
  - assessmentMethod: how this outcome will be evaluated
  - complexityLevel: beginner/intermediate
  - relatedConcepts: array of related concepts

## Entity: Experiment Guide
- **Fields**:
  - guideId: unique identifier
  - title: string
  - chapterId: associated chapter
  - objective: what the experiment is meant to demonstrate
  - requiredMaterials: list of physical and digital resources
  - safetyRequirements: list of safety rules to follow
  - procedure: step-by-step instructions
  - simulationAlternative: alternative procedure using simulation software
  - expectedResults: what students should observe
  - troubleshootingTips: common issues and solutions
  - timeEstimate: estimated duration

## Entity: Safety Rule
- **Fields**:
  - ruleId: unique identifier
  - title: short descriptive title
  - description: detailed explanation of the safety requirement
  - severity: critical/warning/caution
  - applicableExperiments: array of experiment IDs
  - equipmentSpecific: boolean
  - consequences: potential hazards if not followed

## Entity: Student Progress
- **Fields**:
  - studentId: unique identifier
  - chapterCompletions: array of completed chapters with timestamps
  - experimentCompletions: array of completed experiments with timestamps
  - assessmentScores: array of scores for knowledge checks
  - learningOutcomeAchievements: array of achieved learning outcomes
  - currentChapter: current chapter in progress
  - overallProgress: percentage completion

## Entity: Resource
- **Fields**:
  - resourceId: unique identifier
  - title: descriptive title
  - type: reference/link/video/tool
  - url: location of the resource
  - description: brief explanation of what the resource contains
  - targetAudience: beginner/intermediate
  - relatedChapters: array of chapter IDs
  - relatedConcepts: array of concept tags
  - difficultyLevel: 1-5 scale

## Relationships:
- One Chapter contains many Learning Outcomes
- One Chapter contains many Experiment Guides
- One Chapter contains many Safety Rules
- One Chapter contains many Resources
- One Student Progress tracks many Chapter Completions
- One Student Progress tracks many Experiment Completions
- One Student Progress tracks many Assessment Scores
- One Experiment Guide may reference many Safety Rules
- Many Resources can be related to one or more Chapters