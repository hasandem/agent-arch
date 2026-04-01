# Policy Matrix

Use this matrix when the agent is evaluating commit, push, and PR:

- Class A: `allow` for direct PR when local validation passes
- Class B: `ask` before PR, and require local validation
- Class C: `deny` for direct PR; create issue first

Protected areas such as `motivasjon/prinsipper/`, `strategi/`, `sikkerhet/`, and roadmaps always require stricter review than regular documentation.
