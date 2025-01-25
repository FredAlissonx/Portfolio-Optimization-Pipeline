import yaml
import logging
import logging.config
import os
from typing import Optional

class LoggingSetup:
    """
    A utility class for configuring and managing logging using a YAML-based configuration.

    Attributes
    ----------
    _is_configured : bool
        Indicates if logging has already been configured.
    _DEFAULT_CONFIG_PATH : str
        Default path to the logging configuration file (from the environment variable).

    Methods
    -------
    _ensure_logs_directory_exists:
        Create if logs directory does not exist.
    _setup_logging(config_path: Optional[str] = None) -> None
        Configures logging using a YAML file or falls back to basic configuration.
    get_logger(logger_name: str) -> logging.Logger
        Retrieves a logger instance by its name.
    get_data_pipeline_logger() -> logging.Logger
        Returns a logger for data pipeline tasks.
    get_bronze_logger() -> logging.Logger
        Returns a logger for "bronze" tasks in the data pipeline.
    get_silver_logger() -> logging.Logger
        Returns a logger for "silver" tasks in the data pipeline.
    get_gold_logger() -> logging.Logger
        Returns a logger for "gold" tasks in the data pipeline.
    """
    _is_configured: bool = False
    _DEFAULT_CONFIG_PATH: Optional[str] = os.getenv("LOGGING_CONFIG_PATH")

    @classmethod
    def _ensure_logs_directory_exists(cls):
        """Ensure the logs directory exists. If it does not, it creates a directory logs"""
        logs_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
            
    @classmethod
    def _setup_logging(cls, config_path: Optional[str] = None) -> None:
        """
        Configures logging using a YAML file or falls back to basic configuration.

        Parameters
        ----------
        config_path : Optional[str]
            Path to the YAML logging configuration file. Defaults to `_DEFAULT_CONFIG_PATH`.

        Notes
        -----
        If the configuration file is missing or invalid, a basic configuration with WARNING level is applied.
        """
        if cls._is_configured:
            return

        config_path = config_path or cls._DEFAULT_CONFIG_PATH

        if not config_path:
            raise ValueError(
                "Logging configuration path is not set. Ensure the LOGGING_CONFIG_PATH environment variable is defined."
            )

        if not os.path.exists(config_path):
            logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
            logging.warning(f"Logging configuration file not found at {config_path}. Using basic configuration.")
            cls._is_configured = True
            return

        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                if not isinstance(config, dict):
                    raise ValueError("Malformed logging configuration file.")
            
            cls._ensure_logs_directory_exists()
            
            logging.config.dictConfig(config)
            logging.info(f"Logging setup complete using configuration from: {config_path}")
        except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
            logging.basicConfig(level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s")
            logging.warning(f"Failed to load logging configuration from {config_path}: {e}. Using basic configuration.")
        finally:
            cls._is_configured = True

    @classmethod
    def get_logger(cls, logger_name: str) -> logging.Logger:
        """
        Retrieves a logger instance by its name.

        Parameters
        ----------
        logger_name : str
            The name of the logger to retrieve.

        Returns
        -------
        logging.Logger
            A configured logger instance.
        """
        if not cls._is_configured:
            cls._setup_logging()
        return logging.getLogger(logger_name)

    @classmethod
    def get_data_pipeline_logger(cls) -> logging.Logger:
        """Returns a logger for data pipeline tasks."""
        return cls.get_logger("data_pipeline")

    @classmethod
    def get_bronze_logger(cls) -> logging.Logger:
        """Returns a logger for "bronze" tasks in the data pipeline."""
        return cls.get_logger("data_pipeline_bronze")

    @classmethod
    def get_silver_logger(cls) -> logging.Logger:
        """Returns a logger for "silver" tasks in the data pipeline."""
        return cls.get_logger("data_pipeline_silver")

    @classmethod
    def get_gold_logger(cls) -> logging.Logger:
        """Returns a logger for "gold" tasks in the data pipeline."""
        return cls.get_logger("data_pipeline_gold")
