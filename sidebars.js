// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Chapters',
      items: [
        'chapters/intro/chapter1-intro',
        'chapters/fundamentals/chapter2-fundamentals',
        'chapters/perception/chapter3-perception',
        'chapters/control/chapter4-control',
        'chapters/locomotion/chapter5-locomotion',
        'chapters/cognition/chapter6-cognition',
      ],
    },
    {
      type: 'category',
      label: 'Experiments',
      items: [
        {
          type: 'category',
          label: 'Hardware Experiments',
          items: [
            'experiments/hardware/exp1-basic-control',
            'experiments/hardware/exp2-sensor-integration',
            'experiments/hardware/exp3-locomotion-basics',
            'experiments/hardware/exp4-perception-system',
            'experiments/hardware/exp5-basic-cognition',
          ],
        },
        {
          type: 'category',
          label: 'Simulation Experiments',
          items: [
            'experiments/simulation/sim-exp1-basic-control',
            'experiments/simulation/sim-exp2-sensor-integration',
            'experiments/simulation/sim-exp3-locomotion-basics',
            'experiments/simulation/sim-exp4-perception-system',
            'experiments/simulation/sim-exp5-basic-cognition',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Safety Guidelines',
      items: [
        'safety-guidelines/general-safety',
        'safety-guidelines/hardware-safety',
        'safety-guidelines/electrical-safety',
        'safety-guidelines/emergency-procedures',
      ],
    },
    {
      type: 'category',
      label: 'Resources',
      items: [
        'resources/supplementary',
      ],
    }
  ],
};

export default sidebars;