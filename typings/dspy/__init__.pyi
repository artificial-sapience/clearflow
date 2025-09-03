from typing import Any

from _typeshed import Incomplete
from dspy.__metadata__ import __author_email__ as __author_email__
from dspy.__metadata__ import __description__ as __description__
from dspy.__metadata__ import __url__ as __url__
from dspy.__metadata__ import __version__ as __version__
from dspy.adapters import Adapter as Adapter
from dspy.adapters import Audio as Audio
from dspy.adapters import ChatAdapter as ChatAdapter
from dspy.adapters import Code as Code
from dspy.adapters import History as History
from dspy.adapters import Image as Image
from dspy.adapters import JSONAdapter as JSONAdapter
from dspy.adapters import Tool as Tool
from dspy.adapters import ToolCalls as ToolCalls
from dspy.adapters import TwoStepAdapter as TwoStepAdapter
from dspy.adapters import Type as Type
from dspy.adapters import XMLAdapter as XMLAdapter
from dspy.clients import *
from dspy.clients import DSPY_CACHE as DSPY_CACHE
from dspy.dsp.colbertv2 import ColBERTv2 as ColBERTv2
from dspy.dsp.utils.settings import settings as settings
from dspy.evaluate import Evaluate as Evaluate
from dspy.predict import *
from dspy.primitives import *
from dspy.retrievers import *
from dspy.signatures import *
from dspy.streaming.streamify import streamify as streamify
from dspy.teleprompt import *
from dspy.utils.asyncify import asyncify as asyncify
from dspy.utils.logging_utils import configure_dspy_loggers as configure_dspy_loggers
from dspy.utils.logging_utils import disable_logging as disable_logging
from dspy.utils.logging_utils import enable_logging as enable_logging
from dspy.utils.saving import load as load
from dspy.utils.syncify import syncify as syncify
from dspy.utils.usage_tracker import track_usage as track_usage

configure: Incomplete
context: Incomplete
BootstrapRS = BootstrapFewShotWithRandomSearch
cache = DSPY_CACHE
