from arcade_tdk import ToolCatalog
from arcade_evals import (
    EvalRubric,
    EvalSuite,
    ExpectedToolCall,
    tool_eval,
)
from arcade_evals.critic import SimilarityCritic

import domain_name_toolkit

# Evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.85,
    warn_threshold=0.95,
)


catalog = ToolCatalog()
catalog.add_module(domain_name_toolkit)


@tool_eval()
def domain_name_toolkit_eval_suite() -> EvalSuite:
    suite = EvalSuite(
        name="domain_name_toolkit Tools Evaluation",
        system_message=(
            "You are an AI assistant with access to domain_name_toolkit tools. "
            "Use them to help the user with their tasks."
        ),
        catalog=catalog,
        rubric=rubric,
    )

    suite.add_case(
        name="Check domain expiry",
        user_message="When does example.com expire?",
        expected_tool_calls=[
            ExpectedToolCall(func="check_domain_expiry", args={"domain": "example.com"})
        ],
        rubric=rubric,
        critics=[
            SimilarityCritic(critic_field="domain", weight=0.5),
        ],
        additional_messages=[
            {
                "role": "user",
                "content": "I need to know the expiration date for example.com",
            },
            {
                "role": "assistant",
                "content": "I'll check the domain expiration for you.",
            },
        ],
    )

    return suite
