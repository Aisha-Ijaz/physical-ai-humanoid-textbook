---
title: Locomotion
sidebar_position: 5
description: Understanding how humanoid robots achieve various forms of locomotion
---

# Locomotion

## Learning Outcomes

By the end of this chapter, you should be able to:
- Explain the principles of bipedal walking in humanoid robots
- Understand different locomotion patterns and gaits
- Analyze the mathematical models used in humanoid locomotion
- Discuss the challenges of locomotion on various terrains
- Appreciate the integration of perception and control for locomotion

## Introduction to Locomotion in Humanoid Robots

Locomotion is one of the most complex and impressive capabilities of humanoid robots. Unlike wheeled robots, humanoid robots must manage their entire body to move through space while maintaining balance and stability. This requires sophisticated coordination between perception, control, and mechanical systems.

## Principles of Bipedal Walking

### Key Concepts

Bipedal walking involves moving forward using two legs. The challenges include:

- **Intermittent Support**: Only one or both feet are in contact with the ground
- **Dynamic Balance**: The center of mass must be managed in real-time
- **Energy Efficiency**: Walking should be as efficient as possible
- **Stability**: The system must be robust to disturbances

### Gait Phases

Bipedal walking is characterized by two main phases:

#### Single Support Phase
- Only one foot is in contact with the ground
- The stance leg supports the entire body
- The swing leg moves forward to prepare for next support

#### Double Support Phase
- Both feet are in contact with the ground
- Weight transfers from the trailing leg to the leading leg
- Typically occurs during the transition between steps

### Step Parameters

Key parameters that characterize walking include:
- **Step Length**: Distance between consecutive foot placements
- **Step Width**: Lateral distance between feet
- **Step Time**: Duration of a complete step cycle
- **Walking Speed**: Forward velocity of the body

## Mathematical Models of Bipedal Walking

### Inverted Pendulum Model

The simplest model treats the robot as a point mass on a massless leg. This model describes the basic relationship between center of mass position and ground reaction forces.

### Linear Inverted Pendulum Model (LIPM)

This model assumes the center of mass height remains constant, simplifying the dynamic equations while still capturing the essential dynamics of bipedal walking.

### Capture Point

The capture point indicates where a robot must step to come to a stop. It's calculated based on the current center of mass state.

## Walking Pattern Generation

### Preview Control

Preview control uses future reference trajectories to generate stable walking patterns.

### Divergent Component of Motion (DCM)

The DCM is used to plan walking trajectories and represents the point to which the robot will converge if no further steps are taken.

### Footstep Planning

Planning where to place feet is crucial for stable locomotion:
- Consider terrain characteristics
- Maintain balance throughout the gait cycle
- Optimize for efficiency and stability

## Advanced Locomotion Techniques

### Walking Stabilization

Modern humanoid robots use various techniques to maintain stable walking:

#### Feedback Control
- Monitor ZMP position relative to support polygon
- Adjust ankle torques to maintain balance
- Modify step timing and placement as needed

#### Compliance Control
- Use compliant actuators for natural interaction
- Adapt to ground irregularities
- Reduce impact forces during foot landing

### Terrain Adaptation

Humanoid robots must adapt to various terrains:

#### Flat Ground Walking
- Regular gait patterns
- Predictable contact conditions
- Optimal efficiency

#### Rough Terrain
- Variable step placement
- Adjusted gait parameters
- Enhanced perception requirements

#### Stairs and Curbs
- Discrete height changes
- Modified joint trajectories
- Careful control of center of mass

### Dynamic Locomotion

Beyond walking, humanoid robots can achieve:

#### Running
- Controlled falling and catching cycles
- Higher speeds at the cost of stability
- Complex coordination of limbs

#### Jumping
- Brief flight phases
- High peak forces during takeoff and landing
- Precise timing and balance control

## Challenges in Locomotion

### Balance Maintenance

Maintaining balance during locomotion is particularly challenging when:
- External disturbances occur
- Terrain is uneven or slippery
- Robot carries varying loads

### Computational Requirements

Real-time gait generation and control require:
- Fast optimization algorithms
- Efficient dynamic simulation
- Rapid feedback control

### Mechanical Limitations

Physical constraints include:
- Actuator power and speed limits
- Range of motion in joints
- Weight and size constraints

### Energy Efficiency

Achieving human-like efficiency requires:
- Optimal trajectory planning
- Efficient actuator usage
- Recovery of energy during walking

## Integration with Perception and Control

### Visual Feedback for Locomotion

Vision systems can assist locomotion by:
- Detecting obstacles in the path
- Identifying suitable footstep locations
- Recognizing terrain properties

### Multi-Sensory Integration

Locomotion control typically integrates:
- Proprioceptive sensors (joint encoders, IMUs)
- Contact sensors (force/torque, tactile)
- Exteroceptive sensors (cameras, LIDAR)

## Knowledge Check

1. Explain the difference between single support and double support phases in walking.
2. Describe the Linear Inverted Pendulum Model and its application in humanoid locomotion.
3. What are the key challenges in achieving stable locomotion for humanoid robots?

## Exercises

1. Calculate the required step length for a humanoid robot with leg length 0.8m walking at 1 m/s with a step time of 1.2 seconds.
2. Discuss how a humanoid robot might adapt its gait to walk on a slippery surface compared to normal ground.

## Next Steps

In the following chapter, we will explore cognition and learning systems that enable humanoid robots to perceive, reason, and learn from their experiences, completing our foundational understanding of humanoid robotics.