import logging

logger = logging.getLogger("Cleanup")
logger.setLevel(logging.DEBUG)
smatter = logging.Formatter("%(message)s")
fmatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# Console Handler
shandle = logging.StreamHandler()
shandle.setLevel(logging.INFO)
shandle.setFormatter(smatter)
logger.addHandler(shandle)
# File Handler
fhandle = logging.FileHandler("cleanup.log")
fhandle.setLevel(logging.DEBUG)
fhandle.setFormatter(fmatter)
logger.addHandler(fhandle)
