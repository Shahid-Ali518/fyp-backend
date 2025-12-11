from enum import Enum

class Options(Enum):
    very_low = "Very Low"
    low = "Low"
    neutral = "Neutral"
    medium = "Medium"
    high = "High"

OPTION_WEIGHTAGE = {
    Options.very_low: 1,
    Options.low: 2,
    Options.neutral: 3,
    Options.medium: 4,
    Options.high: 5,
}

OPTION_KEYWORDS = {
    Options.very_low: ["very low", "extremely low", "hardly", "almost none", "barely"],
    Options.low: ["low", "a little", "a bit", "slightly", "not much"],
    Options.neutral: ["neutral", "ok", "average", "so-so", "fine", "medium low/high"],
    Options.medium: ["medium", "moderate", "middle", "somewhat", "not too much"],
    Options.high: ["high", "very high", "a lot", "strongly", "extremely"]
}
