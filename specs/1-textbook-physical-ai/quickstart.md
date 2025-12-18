# Quickstart Guide: Physical AI & Humanoid Robotics Textbook

## Getting Started

This quickstart guide will help you get up and running with the Physical AI & Humanoid Robotics textbook project.

### Prerequisites

- Git installed on your system
- Node.js v18+ installed
- Basic familiarity with command-line tools

### Installation Steps

1. Clone the repository:
   ```
   git clone [repository-url]
   cd [repository-name]
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Open your browser to [http://localhost:3000](http://localhost:3000) to view the textbook.

### Building for Production

To create a production-ready build of the textbook:

```
npm run build
```

This will generate static files in the `build/` directory that can be deployed to any static hosting service.

### Key Concepts

The textbook is organized into chapters that progressively build complexity, starting with fundamental concepts and advancing to more sophisticated topics in humanoid robotics. Each chapter includes:

- Core concepts with visual aids
- Hands-on experiment guidelines (both physical and simulation alternatives)
- Knowledge checks to assess your understanding
- Safety guidelines for practical work
- References for further exploration

### First Steps

1. Begin with Chapter 1: "Introduction to Physical AI" to establish foundational concepts.
2. Complete the knowledge checks at the end of each section to validate your understanding.
3. Try the hands-on experiments using either physical hardware or simulation tools (instructions provided for both).
4. Follow all safety guidelines when performing experiments.

### Navigation

- Use the sidebar to navigate between chapters
- Use the search function to find specific topics
- Use the "Next" and "Previous" buttons at the bottom of each page to move through chapters sequentially
- Access supplementary resources through the "Resources" link in the navigation

### Development Workflow

When contributing to the textbook:

1. Create a new branch for your changes
2. Make your modifications to the appropriate markdown files in the `docs/` directory
3. Test your changes by running `npm start`
4. Commit your changes with clear, descriptive messages
5. Push your branch and create a pull request

### Deploying Your Own Instance

To deploy this textbook to GitHub Pages or another static site hosting service:

1. Update the `url`, `baseUrl`, and `projectName` fields in `docusaurus.config.js`
2. Run `npm run deploy` for GitHub Pages (requires proper configuration)
3. For other platforms, build with `npm run build` and upload the `build/` directory

### Need Help?

If you encounter issues or have questions:
- Check the FAQ section in Chapter 0
- Review the troubleshooting tips in the experiment guides
- Consult the additional resources provided with each chapter