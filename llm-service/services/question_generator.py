import json
import uuid
import logging
import re
from typing import Dict, Optional
from services.claude_client import ClaudeClient

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates interview questions using Claude"""

    def __init__(self, claude_client: ClaudeClient):
        self.client = claude_client

    async def generate(
        self, 
        topic: str, 
        difficulty: str, 
        position: int,
        jd_context: Optional[str] = None
    ) -> Dict:
        """Generate an interview question based on topic or job description."""

        # Determine difficulty level for the question
        if position == 0:
            target_difficulty = "easy"
        elif position == 1:
            target_difficulty = "medium"
        else:
            target_difficulty = "hard"

        # Build system prompt based on whether JD context is provided
        if topic == "dynamic" and jd_context:
            logger.info(f"Using JD-based prompt with context: {jd_context[:100]}...")
            system_prompt = self._build_jd_based_prompt(jd_context, difficulty, target_difficulty)
        else:
            logger.info(f"Using topic-based prompt for: {topic}")
            system_prompt = self._build_topic_based_prompt(topic, difficulty, target_difficulty)

        user_message = f"Generate a {target_difficulty} question for position {position} in the interview."

        response = await self.client.generate_text(
            system_prompt=system_prompt,
            user_message=user_message,
            temperature=0.8
        )
        
        logger.info(f"Claude response (first 500 chars): {response[:500] if response else 'None'}")

        # Try to extract JSON from response
        question_data = self._extract_json(response)
        
        if question_data:
            return {
                "id": str(uuid.uuid4()),
                "stem": question_data.get("stem", ""),
                "difficulty": target_difficulty,
                "followUps": question_data.get("followUps", []),
                "evaluationHints": question_data.get("evaluationHints", []),
                "redFlags": question_data.get("redFlags", []),
                "asked": False,
                "askedAt": None
            }
        else:
            logger.warning(f"Failed to parse JSON, using fallback. Response was: {response[:300]}")
            return self._get_fallback_question(topic, target_difficulty)
    
    def _extract_json(self, response: str) -> Optional[Dict]:
        """Extract JSON from response, handling markdown code blocks."""
        if not response:
            return None
            
        # First try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in markdown code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find raw JSON object
        json_match = re.search(r'\{[^{}]*"stem"[^{}]*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # Try finding JSON with nested objects (for followUps arrays)
        json_match = re.search(r'\{.*"stem".*"followUps".*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None

    def _build_topic_based_prompt(self, topic: str, difficulty: str, target_difficulty: str) -> str:
        """Build prompt for standard topic-based interviews."""
        
        # Special handling for DSA/algorithms topics
        if topic.lower() in ['algorithms', 'dsa', 'data_structures', 'coding']:
            return self._build_dsa_prompt(difficulty, target_difficulty)
        
        return f"""You are an expert technical interviewer creating questions for {topic} interviews.
Generate ONE high-quality interview question suitable for a {difficulty} level candidate.

The question should be {target_difficulty} difficulty level.

Return your response as valid JSON with this structure:
{{
  "stem": "The main question text",
  "followUps": ["Follow-up question 1", "Follow-up question 2"],
  "evaluationHints": ["Expected approach 1", "Expected approach 2"],
  "redFlags": ["Common mistake 1", "Common mistake 2"]
}}

Make the question practical and relevant to real-world scenarios."""

    def _build_dsa_prompt(self, difficulty: str, target_difficulty: str) -> str:
        """Build prompt specifically for DSA/Algorithm questions with detailed problem statements."""
        return f"""You are an expert technical interviewer at a top tech company (Google/Meta/Amazon level).
You are creating a DSA coding problem for a {difficulty} level candidate.

## CRITICAL REQUIREMENTS FOR THE QUESTION:

1. **DETAILED PROBLEM STATEMENT**: Write a complete, specific problem like LeetCode/HackerRank style:
   - Clear problem description with context
   - Explicit input format and constraints
   - Explicit output format
   - 2-3 concrete examples with input/output
   - Edge cases mentioned in constraints

2. **CONVERSATIONAL OPENING**: Start with a brief friendly intro like:
   - "Alright, let's work through a coding problem together."
   - "Here's an interesting problem I'd like you to solve."
   - "Let me give you a coding challenge."

3. **END WITH UNDERSTANDING CHECK**: Always end with:
   - "Does the problem make sense? Feel free to ask any clarifying questions before we proceed."
   - "Take a moment to understand the problem. Let me know if anything is unclear."

## DIFFICULTY: {target_difficulty}

For {target_difficulty} level:
{"- Arrays, strings, basic hash maps, simple loops" if target_difficulty == "easy" else ""}
{"- Two pointers, sliding window, BFS/DFS, binary search, medium DP" if target_difficulty == "medium" else ""}
{"- Advanced DP, graphs, tries, segment trees, complex algorithms" if target_difficulty == "hard" else ""}

## EXAMPLE FORMAT FOR STEM:

"Alright, let's work on a coding problem together.

**Problem: [Problem Name]**

[2-3 sentence problem description with real-world context if applicable]

**Input:**
- [Describe input format]
- Constraints: [List constraints like 1 <= n <= 10^5]

**Output:**
- [Describe expected output]

**Examples:**

Example 1:
Input: [specific input]
Output: [specific output]
Explanation: [brief explanation]

Example 2:
Input: [specific input]
Output: [specific output]

Does this problem make sense to you? Feel free to ask any clarifying questions before you start."

Return your response as valid JSON:
{{
  "stem": "[Full detailed problem as shown above]",
  "followUps": [
    "What's your initial approach? Walk me through your thinking.",
    "Can you analyze the time and space complexity?",
    "How would you handle [specific edge case]?",
    "Can you optimize this further?"
  ],
  "evaluationHints": [
    "[Optimal algorithm/approach]",
    "[Expected time complexity]",
    "[Expected space complexity]",
    "[Key insight needed]"
  ],
  "redFlags": [
    "Jumps to coding without understanding the problem",
    "Cannot identify the pattern/algorithm type",
    "Ignores edge cases",
    "Cannot analyze complexity"
  ]
}}"""

    def _build_jd_based_prompt(self, jd_context: str, difficulty: str, target_difficulty: str) -> str:
        """Build prompt for job description-based interviews."""
        return f"""You are an expert interviewer creating questions based on a specific job description.

JOB CONTEXT:
{jd_context}

Generate ONE highly relevant interview question that:
1. Tests skills specifically mentioned in the job description
2. Is appropriate for a {difficulty} level candidate
3. Reflects real scenarios they would face in this role
4. Has {target_difficulty} difficulty level

Return your response as valid JSON with this structure:
{{
  "stem": "The main question text - make it specific to the job requirements",
  "followUps": ["Follow-up question 1", "Follow-up question 2"],
  "evaluationHints": ["What a good answer should include based on job requirements"],
  "redFlags": ["Signs the candidate may not be suitable for this specific role"]
}}

Focus on the most critical skills and responsibilities from the job description."""

    def _get_fallback_question(self, topic: str, difficulty: str) -> Dict:
        """Fallback question if generation fails - with detailed DSA problems"""
        
        fallback_questions = {
            "algorithms": {
                "easy": {
                    "stem": """Alright, let's work on a coding problem together.

**Problem: Two Sum**

Given an array of integers `nums` and an integer `target`, return the indices of the two numbers that add up to the target.

**Input:**
- An array of integers `nums` (2 <= nums.length <= 10^4)
- An integer `target`
- Each input has exactly one solution
- You may not use the same element twice

**Output:**
- Return an array of two indices [i, j] where nums[i] + nums[j] == target

**Examples:**

Example 1:
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1]
Explanation: nums[0] + nums[1] = 2 + 7 = 9

Example 2:
Input: nums = [3, 2, 4], target = 6
Output: [1, 2]

Example 3:
Input: nums = [3, 3], target = 6
Output: [0, 1]

Does this problem make sense to you? Feel free to ask any clarifying questions before you start.""",
                    "followUps": [
                        "What's your initial approach? Walk me through your thinking.",
                        "What's the time and space complexity of your solution?",
                        "Can you think of a more optimal approach?",
                        "What happens if there are duplicate values?"
                    ],
                    "evaluationHints": [
                        "Optimal: Hash map approach O(n) time, O(n) space",
                        "Brute force: O(n²) time, O(1) space",
                        "Should handle duplicates correctly",
                        "Return indices, not values"
                    ],
                    "redFlags": [
                        "Jumps to coding without understanding",
                        "O(n²) without discussing optimization",
                        "Returns values instead of indices",
                        "Doesn't consider edge cases"
                    ]
                },
                "medium": {
                    "stem": """Let's work through a classic problem together.

**Problem: Longest Substring Without Repeating Characters**

Given a string `s`, find the length of the longest substring without repeating characters.

**Input:**
- A string `s` consisting of English letters, digits, symbols, and spaces
- 0 <= s.length <= 5 * 10^4

**Output:**
- An integer representing the length of the longest substring without duplicate characters

**Examples:**

Example 1:
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with length 3.

Example 2:
Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with length 1.

Example 3:
Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with length 3. Note that "pwke" is a subsequence, not a substring.

Does this make sense? Let me know if you have any questions about the problem.""",
                    "followUps": [
                        "What approach are you thinking of using?",
                        "How would you keep track of characters you've seen?",
                        "What's the time complexity of your solution?",
                        "How do you handle the case when you find a duplicate?"
                    ],
                    "evaluationHints": [
                        "Optimal: Sliding window with hash set/map O(n)",
                        "Should correctly shrink window on duplicates",
                        "Handle empty string edge case",
                        "Understand difference between substring and subsequence"
                    ],
                    "redFlags": [
                        "Doesn't know sliding window technique",
                        "Confuses substring with subsequence",
                        "O(n²) or worse without optimization discussion",
                        "Cannot handle the window shrinking logic"
                    ]
                },
                "hard": {
                    "stem": """Here's a challenging problem. Take your time with this one.

**Problem: LRU Cache**

Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.

Implement the `LRUCache` class:
- `LRUCache(int capacity)` - Initialize the cache with positive capacity
- `int get(int key)` - Return the value if key exists, otherwise return -1
- `void put(int key, int value)` - Update or insert the value. If capacity is exceeded, evict the least recently used key.

**Constraints:**
- 1 <= capacity <= 3000
- 0 <= key <= 10^4
- 0 <= value <= 10^5
- At most 2 * 10^5 calls to get and put
- **Both get and put must run in O(1) average time complexity**

**Examples:**

Input:
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]

Output: [null, null, null, 1, null, -1, null, -1, 3, 4]

Explanation:
LRUCache cache = new LRUCache(2);
cache.put(1, 1);    // cache is {1=1}
cache.put(2, 2);    // cache is {1=1, 2=2}
cache.get(1);       // returns 1, cache is {2=2, 1=1}
cache.put(3, 3);    // evicts key 2, cache is {1=1, 3=3}
cache.get(2);       // returns -1 (not found)
cache.put(4, 4);    // evicts key 1, cache is {3=3, 4=4}
cache.get(1);       // returns -1 (not found)
cache.get(3);       // returns 3
cache.get(4);       // returns 4

Take a moment to think about the data structures you'd need. Does the problem make sense?""",
                    "followUps": [
                        "What data structures would give us O(1) for both operations?",
                        "How do you track which element is least recently used?",
                        "Walk me through what happens when the cache is full and we add a new element.",
                        "Can you trace through the example to verify your design?"
                    ],
                    "evaluationHints": [
                        "Optimal: HashMap + Doubly Linked List",
                        "HashMap for O(1) lookup",
                        "Doubly linked list for O(1) insertion/deletion",
                        "Move accessed items to front, remove from back"
                    ],
                    "redFlags": [
                        "Doesn't achieve O(1) for both operations",
                        "Uses only a single data structure",
                        "Cannot explain the eviction logic",
                        "Doesn't understand doubly linked list benefits"
                    ]
                }
            },
            "system_design": {
                "easy": {
                    "stem": """Let's discuss a system design problem.

**Problem: Design a URL Shortening Service (like bit.ly)**

Design a service that takes a long URL and returns a shortened version. When users visit the short URL, they should be redirected to the original.

**Requirements:**
- Generate short URLs that are easy to share
- Handle high read traffic (many redirects)
- URLs should be unique
- Optional: Custom short URLs, analytics, expiration

**Questions to consider:**
- How will you generate unique short codes?
- How will you store the mappings?
- How will you handle high traffic?

Let's start by discussing your high-level approach. What components would you need?""",
                    "followUps": [
                        "How would you generate unique short codes?",
                        "What database would you use and why?",
                        "How would you handle 10x traffic growth?",
                        "What about URL collisions?"
                    ],
                    "evaluationHints": [
                        "Base62 encoding for short codes",
                        "Database with caching (Redis)",
                        "Horizontal scaling discussion",
                        "Load balancing and CDN"
                    ],
                    "redFlags": [
                        "No scalability considerations",
                        "Single point of failure",
                        "No caching strategy",
                        "Cannot estimate storage needs"
                    ]
                }
            },
            "behavioral": {
                "easy": {
                    "stem": "Tell me about a time when you had to work with a difficult team member. How did you handle the situation?",
                    "followUps": [
                        "What was the outcome?",
                        "What would you do differently looking back?",
                        "What did you learn from this experience?"
                    ],
                    "evaluationHints": [
                        "Uses STAR method",
                        "Shows empathy",
                        "Takes responsibility",
                        "Focuses on resolution"
                    ],
                    "redFlags": [
                        "Blames others entirely",
                        "No specific example",
                        "No reflection or learning"
                    ]
                }
            }
        }

        # Get fallback for topic/difficulty, with proper defaults
        topic_key = topic.lower()
        if topic_key in ['dsa', 'coding', 'data_structures']:
            topic_key = 'algorithms'
            
        topic_questions = fallback_questions.get(topic_key, fallback_questions.get("algorithms", {}))
        question = topic_questions.get(difficulty, topic_questions.get("easy", {
            "stem": """Let's work on a problem together.

**Problem: Find Maximum in Array**

Given an array of integers, find and return the maximum value.

**Input:** An array of integers (1 <= length <= 1000)
**Output:** The maximum integer in the array

**Example:**
Input: [3, 1, 4, 1, 5, 9, 2, 6]
Output: 9

Does this make sense? How would you approach it?""",
            "followUps": ["What's the time complexity?", "What if the array is empty?"],
            "evaluationHints": ["O(n) single pass", "Handle edge cases"],
            "redFlags": ["Cannot handle empty array"]
        }))

        return {
            "id": str(uuid.uuid4()),
            "stem": question["stem"],
            "difficulty": difficulty,
            "followUps": question["followUps"],
            "evaluationHints": question["evaluationHints"],
            "redFlags": question["redFlags"],
            "asked": False,
            "askedAt": None
        }
