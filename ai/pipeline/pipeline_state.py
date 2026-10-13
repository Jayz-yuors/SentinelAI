from ai.infrastructure.constants.application_constants import (
    VALID_PIPELINE_STATES
)


class PipelineState:

    def __init__(
        self,
        state: str
    ):

        if state not in VALID_PIPELINE_STATES:

            raise ValueError(
                f"Invalid pipeline state: {state}"
            )

        self._state = state

    def set_state(
        self,
        state: str
    ):

        if state not in VALID_PIPELINE_STATES:

            raise ValueError(
                f"Invalid pipeline state: {state}"
            )

        self._state = state

    def get_state(self):

        return self._state