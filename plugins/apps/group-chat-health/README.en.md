# Group Chat

English | [简体中文](./README.md)

Group Chat is a multi-agent group chat plugin for QwenPaw. It reads the agents that are currently enabled, lets you bring different roles into one conversation, shares the conversation context among them, and coordinates collaboration through intelligent routing and `@` mentions.

## What It Does

- **Create your own groups**: choose one or more existing, enabled QwenPaw agents.
- **Route messages intelligently**: for a regular message, the plugin uses member names, descriptions, and recent context to invite a suitable member to respond.
- **Address specific members**: type `@` or click a quick member chip. One message can mention multiple agents in order.
- **Hand off between members**: an agent can `@` another group member and invite them to continue.
- **Support complete conversations**: quote messages, attach files, retry failed requests, and keep durable chat history.
- **Allow proactive participation**: enable it when needed and configure quiet hours, daily limits, and cooldowns.

Each group member keeps its existing persona, model, knowledge, skills, tool permissions, and workspace. The plugin coordinates the group conversation without changing the member's own capabilities.

## Installation

1. In the QwenPaw sidebar, open **Extensions → App Marketplace**.
2. Search for **Group Chat**.
3. Find the app and click Install.
4. Open **Group Chat** after installation.

## How to Use It

1. Create a new group and enter a group name.
2. Select one or more enabled agents as members, then save the group.
3. Send a regular message and let the plugin choose a suitable member to respond.
4. For explicit assignments, type `@member name` or click a quick member chip below the input box.
5. Open **Group Info** to review or change members and configure proactive participation.

## Notes

- The plugin creates an internal **Group Chat Router** agent to select responding members. It does not answer users directly and does not appear in QwenPaw's regular agent selector.
- If multiple agents in a group share the same name, the plugin uses the agent ID as the unique mention name.
- Proactive participation is disabled by default. When it is off, agents respond only after the user sends a message or another member mentions them.
