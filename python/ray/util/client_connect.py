from ray.util.client import ray
from ray.job_config import JobConfig
from ray._private.client_mode_hook import _set_client_hook_status
from ray._private.client_mode_hook import _explicitly_enable_client_mode

from typing import List, Tuple, Dict, Any, Optional

import grpc


def connect(
    conn_str: str,
    secure: bool = False,
    metadata: List[Tuple[str, str]] = None,
    connection_retries: int = 3,
    job_config: JobConfig = None,
    namespace: str = None,
    *,
    ignore_version: bool = False,
    _credentials: Optional[grpc.ChannelCredentials] = None,
    ray_init_kwargs: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if ray.is_connected():
        raise RuntimeError(
            "Ray Client is already connected. Maybe you called "
            'ray.init("ray://<address>") twice by accident?'
        )

    # Pull out metadata from kwargs and put into explicit metadata arg to connect
    if ray_init_kwargs is not None:
        if "metadata" in ray_init_kwargs.keys():
            if metadata is None:
                metadata = []
            metadata = metadata + ray_init_kwargs["metadata"]
            del ray_init_kwargs["metadata"]

    # Enable the same hooks that RAY_CLIENT_MODE does, as calling
    # ray.init("ray://<address>") is specifically for using client mode.
    _set_client_hook_status(True)
    _explicitly_enable_client_mode()

    # TODO(barakmich): https://github.com/ray-project/ray/issues/13274
    # for supporting things like cert_path, ca_path, etc and creating
    # the correct metadata
    conn = ray.connect(
        conn_str,
        job_config=job_config,
        secure=secure,
        metadata=metadata,
        connection_retries=connection_retries,
        namespace=namespace,
        ignore_version=ignore_version,
        _credentials=_credentials,
        ray_init_kwargs=ray_init_kwargs,
    )
    return conn


def disconnect():
    """Disconnects from server; is idempotent."""
    return ray.disconnect()
