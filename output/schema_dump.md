# Database Schema Dump

Connected to Host: `app.gestobra.com` | Database: `gestobra`

## Schema: `public`

### Table: `accessories`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `category` | `character varying` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |

### Table: `ai_jobs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `queue_name` | `text` | `NO` |
| `payload` | `json` | `NO` |
| `status` | `character varying` | `NO` |
| `attempts` | `integer` | `NO` |
| `max_attempts` | `integer` | `NO` |
| `run_at` | `timestamp without time zone` | `NO` |
| `locked_at` | `timestamp without time zone` | `YES` |
| `locked_by` | `text` | `YES` |
| `last_error` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `billing_provisioning_jobs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `stripe_event_id` | `character varying` | `NO` |
| `stripe_checkout_session_id` | `character varying` | `NO` |
| `event_type` | `character varying` | `NO` |
| `payload` | `text` | `NO` |
| `status` | `character varying` | `NO` |
| `attempt_count` | `integer` | `NO` |
| `available_at` | `timestamp without time zone` | `NO` |
| `locked_at` | `timestamp without time zone` | `YES` |
| `completed_at` | `timestamp without time zone` | `YES` |
| `last_error` | `text` | `YES` |
| `team_id` | `bigint` | `YES` |
| `invitation_id` | `bigint` | `YES` |
| `created_at` | `timestamp without time zone` | `NO` |
| `updated_at` | `timestamp without time zone` | `NO` |

### Table: `cache`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `key` | `character varying` | `NO` |
| `value` | `text` | `NO` |
| `expiration` | `integer` | `NO` |

### Table: `cache_locks`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `key` | `character varying` | `NO` |
| `owner` | `character varying` | `NO` |
| `expiration` | `integer` | `NO` |

### Table: `cargos`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `channels`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `code` | `character varying` | `NO` |
| `name` | `character varying` | `NO` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `checkpoint_blobs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `thread_id` | `text` | `NO` |
| `checkpoint_ns` | `text` | `NO` |
| `channel` | `text` | `NO` |
| `version` | `text` | `NO` |
| `type` | `text` | `NO` |
| `blob` | `bytea` | `YES` |

### Table: `checkpoint_migrations`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `v` | `integer` | `NO` |

### Table: `checkpoint_writes`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `thread_id` | `text` | `NO` |
| `checkpoint_ns` | `text` | `NO` |
| `checkpoint_id` | `text` | `NO` |
| `task_id` | `text` | `NO` |
| `idx` | `integer` | `NO` |
| `channel` | `text` | `NO` |
| `type` | `text` | `YES` |
| `blob` | `bytea` | `NO` |
| `task_path` | `text` | `NO` |

### Table: `checkpoints`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `thread_id` | `text` | `NO` |
| `checkpoint_ns` | `text` | `NO` |
| `checkpoint_id` | `text` | `NO` |
| `parent_checkpoint_id` | `text` | `YES` |
| `type` | `text` | `YES` |
| `checkpoint` | `jsonb` | `NO` |
| `metadata` | `jsonb` | `NO` |

### Table: `cities`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `state_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |

### Table: `companies`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `tax_id` | `character varying` | `NO` |
| `country_code` | `character varying` | `NO` |
| `address` | `character varying` | `NO` |
| `state` | `character varying` | `NO` |
| `city` | `character varying` | `NO` |
| `postal_code` | `character varying` | `NO` |
| `phone` | `character varying` | `YES` |
| `email` | `character varying` | `YES` |
| `website` | `character varying` | `YES` |
| `iban` | `character varying` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |

### Table: `countries`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `code` | `character varying` | `NO` |
| `name` | `character varying` | `NO` |
| `phone_prefix` | `character varying` | `YES` |

### Table: `daily_sessions`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `session_date` | `date` | `NO` |
| `state` | `character varying` | `NO` |
| `active_task_id` | `bigint` | `YES` |
| `pending_action` | `character varying` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `finished_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `active_task_task_id` | `bigint` | `YES` |
| `active_task_started_at` | `timestamp without time zone` | `YES` |
| `state_context` | `jsonb` | `YES` |
| `hourly_summary_cursor_at` | `timestamp with time zone` | `YES` |
| `active_project_id` | `bigint` | `YES` |
| `active_project_schedule_id` | `bigint` | `YES` |
| `active_project_started_at` | `timestamp with time zone` | `YES` |
| `active_project_imputation_id` | `bigint` | `YES` |

### Table: `failed_jobs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `uuid` | `character varying` | `NO` |
| `connection` | `text` | `NO` |
| `queue` | `text` | `NO` |
| `payload` | `text` | `NO` |
| `exception` | `text` | `NO` |
| `failed_at` | `timestamp without time zone` | `NO` |

### Table: `file_types`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `fileable_type` | `character varying` | `NO` |
| `fileable_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `files`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `storage_disk` | `character varying` | `NO` |
| `storage_path` | `text` | `NO` |
| `original_name` | `text` | `NO` |
| `mime_type` | `character varying` | `NO` |
| `size_bytes` | `bigint` | `NO` |
| `sha256` | `character varying` | `NO` |
| `team_id` | `bigint` | `YES` |
| `file_type_id` | `bigint` | `YES` |
| `uploaded_by_user_id` | `bigint` | `YES` |
| `version` | `integer` | `NO` |
| `is_active` | `boolean` | `NO` |
| `comment` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `flyway_schema_history`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `installed_rank` | `integer` | `NO` |
| `version` | `character varying` | `YES` |
| `description` | `character varying` | `NO` |
| `type` | `character varying` | `NO` |
| `script` | `character varying` | `NO` |
| `checksum` | `integer` | `YES` |
| `installed_by` | `character varying` | `NO` |
| `installed_on` | `timestamp without time zone` | `NO` |
| `execution_time` | `integer` | `NO` |
| `success` | `boolean` | `NO` |

### Table: `invoices`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `provider_id` | `character varying` | `NO` |
| `amount` | `numeric` | `NO` |
| `currency` | `character varying` | `NO` |
| `paid_at` | `timestamp without time zone` | `YES` |
| `pdf_url` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |

### Table: `job_batches`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `character varying` | `NO` |
| `name` | `character varying` | `NO` |
| `total_jobs` | `integer` | `NO` |
| `pending_jobs` | `integer` | `NO` |
| `failed_jobs` | `integer` | `NO` |
| `failed_job_ids` | `text` | `NO` |
| `options` | `text` | `YES` |
| `cancelled_at` | `integer` | `YES` |
| `created_at` | `integer` | `NO` |
| `finished_at` | `integer` | `YES` |

### Table: `jobs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `queue` | `character varying` | `NO` |
| `payload` | `text` | `NO` |
| `attempts` | `smallint` | `NO` |
| `reserved_at` | `integer` | `YES` |
| `available_at` | `integer` | `NO` |
| `created_at` | `integer` | `NO` |

### Table: `message_files`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `message_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `path` | `character varying` | `NO` |
| `mime_type` | `character varying` | `YES` |
| `size` | `bigint` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `messages`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `person_id` | `bigint` | `YES` |
| `contact_name` | `character varying` | `NO` |
| `contact_phone` | `character varying` | `NO` |
| `user_phone` | `character varying` | `YES` |
| `content` | `text` | `NO` |
| `channel` | `character varying` | `NO` |
| `direction` | `character varying` | `NO` |
| `type` | `character varying` | `NO` |
| `ai_summary` | `text` | `YES` |
| `audio_url` | `character varying` | `YES` |
| `call_duration` | `integer` | `YES` |
| `is_read` | `boolean` | `NO` |
| `read_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `migrations`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `integer` | `NO` |
| `migration` | `character varying` | `NO` |
| `batch` | `integer` | `NO` |

### Table: `milestones`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `project_id` | `bigint` | `NO` |
| `title` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `type` | `character varying` | `NO` |
| `milestone_date` | `date` | `NO` |
| `completed` | `boolean` | `NO` |
| `order` | `integer` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |

### Table: `notification_channels`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `notification_id` | `bigint` | `NO` |
| `channel_code` | `character varying` | `NO` |
| `status` | `character varying` | `NO` |
| `external_message_id` | `character varying` | `YES` |
| `error_message` | `text` | `YES` |
| `sent_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `notification_deduplications`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `job_code` | `character varying` | `NO` |
| `rule_code` | `character varying` | `NO` |
| `entity_id` | `character varying` | `NO` |
| `business_date` | `date` | `NO` |
| `sent_at` | `timestamp without time zone` | `NO` |

### Table: `notification_items`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `notification_id` | `bigint` | `NO` |
| `item_type` | `character varying` | `NO` |
| `actor_user_id` | `bigint` | `YES` |
| `actor_person_id` | `bigint` | `YES` |
| `title` | `character varying` | `NO` |
| `body` | `text` | `YES` |
| `happened_at` | `timestamp without time zone` | `NO` |
| `metadata_json` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `notification_job_configs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `job_code` | `character varying` | `NO` |
| `rule_code` | `character varying` | `NO` |
| `cron_expression` | `character varying` | `NO` |
| `enabled` | `boolean` | `NO` |
| `timezone` | `character varying` | `NO` |
| `updated_at` | `timestamp without time zone` | `NO` |
| `config_json` | `text` | `YES` |

### Table: `notification_type_channels`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `notification_type_code` | `character varying` | `NO` |
| `channel_code` | `character varying` | `NO` |
| `default_enabled` | `boolean` | `NO` |
| `mandatory` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `notification_types`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `code` | `character varying` | `NO` |
| `description` | `character varying` | `NO` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `notifications`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `notification_type_code` | `character varying` | `NO` |
| `title` | `character varying` | `NO` |
| `body` | `text` | `NO` |
| `status` | `character varying` | `NO` |
| `priority` | `character varying` | `NO` |
| `metadata_json` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `NO` |
| `sent_at` | `timestamp without time zone` | `YES` |
| `read_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `aggregation_key` | `character varying` | `YES` |
| `aggregation_date` | `date` | `YES` |
| `aggregation_mode` | `character varying` | `YES` |
| `source_entity_type` | `character varying` | `YES` |
| `source_entity_id` | `character varying` | `YES` |
| `last_activity_at` | `timestamp without time zone` | `YES` |
| `event_count` | `integer` | `NO` |
| `payload_json` | `text` | `YES` |

### Table: `password_reset_tokens`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `email` | `character varying` | `NO` |
| `token` | `character varying` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |

### Table: `people`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `company_id` | `bigint` | `YES` |
| `phone` | `character varying` | `YES` |
| `phone_secondary` | `character varying` | `YES` |
| `email` | `character varying` | `YES` |
| `notes` | `text` | `YES` |
| `is_client` | `boolean` | `NO` |
| `is_worker` | `boolean` | `NO` |
| `is_external_worker` | `boolean` | `NO` |
| `is_supplier` | `boolean` | `NO` |
| `user_id` | `bigint` | `YES` |
| `billing_type` | `character varying` | `YES` |
| `language` | `character varying` | `NO` |
| `cargo_id` | `bigint` | `YES` |

### Table: `person_absences`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `start_date` | `date` | `NO` |
| `end_date` | `date` | `NO` |
| `reason` | `character varying` | `NO` |
| `comments` | `text` | `YES` |
| `created_by_user_id` | `bigint` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `person_specialty`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `specialty_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `person_tag`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `tag_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `personal_access_tokens`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `tokenable_type` | `character varying` | `NO` |
| `tokenable_id` | `bigint` | `NO` |
| `name` | `text` | `NO` |
| `token` | `character varying` | `NO` |
| `abilities` | `text` | `YES` |
| `last_used_at` | `timestamp without time zone` | `YES` |
| `expires_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `plan_price_versions`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `plan_id` | `bigint` | `NO` |
| `stripe_price_id` | `character varying` | `YES` |
| `unit_amount` | `bigint` | `NO` |
| `currency` | `character varying` | `NO` |
| `billing_interval` | `character varying` | `NO` |
| `interval_count` | `integer` | `NO` |
| `is_active` | `boolean` | `NO` |
| `sync_status` | `character varying` | `NO` |
| `valid_from` | `timestamp without time zone` | `YES` |
| `valid_to` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `NO` |
| `updated_at` | `timestamp without time zone` | `NO` |

### Table: `planner_report_settings`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `report_date` | `date` | `NO` |
| `send_before_days` | `integer` | `NO` |
| `send_time` | `time without time zone` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `plans`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `price_per_user` | `numeric` | `NO` |
| `currency` | `character varying` | `NO` |
| `limits_json` | `jsonb` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `is_custom` | `boolean` | `NO` |
| `is_active` | `boolean` | `NO` |
| `max_gestors` | `integer` | `NO` |
| `max_operario_jefe` | `integer` | `NO` |
| `max_operarios` | `integer` | `NO` |
| `extra_gestor_price` | `numeric` | `NO` |
| `extra_operario_jefe_price` | `numeric` | `NO` |
| `extra_operario_price` | `numeric` | `NO` |
| `monthly_price` | `numeric` | `NO` |
| `ai_credits_monthly` | `integer` | `NO` |
| `ai_pack_a_credits` | `integer` | `NO` |
| `ai_pack_a_price` | `numeric` | `NO` |
| `ai_pack_b_credits` | `integer` | `NO` |
| `ai_pack_b_price` | `numeric` | `NO` |
| `ai_pack_c_credits` | `integer` | `NO` |
| `ai_pack_c_price` | `numeric` | `NO` |
| `billing_code` | `character varying` | `YES` |
| `stripe_product_id` | `character varying` | `YES` |
| `is_public` | `boolean` | `NO` |

### Table: `project_comments`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `project_id` | `bigint` | `NO` |
| `author_user_id` | `bigint` | `NO` |
| `body` | `text` | `YES` |
| `files` | `jsonb` | `YES` |
| `tags` | `jsonb` | `YES` |
| `created_at` | `timestamp without time zone` | `NO` |
| `updated_at` | `timestamp without time zone` | `NO` |
| `original_body` | `text` | `YES` |
| `parent_comment_id` | `bigint` | `YES` |

### Table: `project_imputations`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `project_id` | `bigint` | `NO` |
| `resource_id` | `bigint` | `NO` |
| `created_by_user_id` | `bigint` | `YES` |
| `type` | `character varying` | `NO` |
| `date` | `date` | `NO` |
| `amount` | `numeric` | `NO` |
| `minutes` | `integer` | `YES` |
| `hourly_rate` | `numeric` | `YES` |
| `file_path` | `character varying` | `YES` |
| `file_name` | `character varying` | `YES` |
| `description` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `task_id` | `bigint` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `finished_at` | `timestamp without time zone` | `YES` |
| `original_minutes` | `integer` | `YES` |
| `is_corrected` | `boolean` | `NO` |
| `correction_reason` | `text` | `YES` |
| `corrected_by_user_id` | `bigint` | `YES` |
| `corrected_at` | `timestamp with time zone` | `YES` |
| `correction_source` | `character varying` | `YES` |

### Table: `project_schedule_resource`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `project_schedule_id` | `bigint` | `NO` |
| `resource_id` | `bigint` | `NO` |
| `is_responsible` | `boolean` | `NO` |
| `shift_minutes` | `integer` | `NO` |
| `notes` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `order_index` | `integer` | `YES` |

### Table: `project_schedules`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `project_id` | `bigint` | `NO` |
| `scheduled_date` | `date` | `NO` |
| `order` | `integer` | `YES` |
| `type` | `character varying` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `project_specialty`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `project_id` | `bigint` | `NO` |
| `specialty_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `project_tag`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `project_id` | `bigint` | `NO` |
| `tag_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `NO` |
| `updated_at` | `timestamp without time zone` | `NO` |

### Table: `projects`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `address` | `character varying` | `YES` |
| `country_code` | `character varying` | `YES` |
| `state` | `character varying` | `YES` |
| `city` | `character varying` | `YES` |
| `postal_code` | `character varying` | `YES` |
| `status` | `character varying` | `NO` |
| `owner_user_id` | `bigint` | `NO` |
| `start_date` | `date` | `YES` |
| `end_date` | `date` | `YES` |
| `actual_end_date` | `date` | `YES` |
| `budget` | `numeric` | `YES` |
| `actual_cost` | `numeric` | `NO` |
| `hourly_rate` | `numeric` | `YES` |
| `project_type` | `character varying` | `YES` |
| `client_person_id` | `bigint` | `YES` |
| `leader_person_id` | `bigint` | `YES` |
| `working_days` | `jsonb` | `YES` |
| `notes` | `text` | `YES` |
| `total_area` | `numeric` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `planner_color` | `character varying` | `YES` |
| `actual_start_date` | `date` | `YES` |

### Table: `reports`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `created_by_user_id` | `bigint` | `NO` |
| `type` | `character varying` | `NO` |
| `status` | `character varying` | `NO` |
| `params_json` | `jsonb` | `YES` |
| `file_id` | `bigint` | `YES` |
| `error_text` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `resources`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `type` | `character varying` | `NO` |
| `name` | `character varying` | `NO` |
| `nickname` | `character varying` | `YES` |
| `hourly_rate` | `numeric` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `daily_capacity_minutes` | `integer` | `YES` |

### Table: `sessions`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `character varying` | `NO` |
| `user_id` | `bigint` | `YES` |
| `ip_address` | `character varying` | `YES` |
| `user_agent` | `text` | `YES` |
| `payload` | `text` | `NO` |
| `last_activity` | `integer` | `NO` |

### Table: `specialties`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `color` | `character varying` | `NO` |
| `icon` | `character varying` | `YES` |
| `description` | `text` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `specialty_task`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `specialty_id` | `bigint` | `NO` |
| `task_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `specialty_task_template`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `task_template_id` | `bigint` | `NO` |
| `specialty_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `specialty_user`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `specialty_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `states`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `country_code` | `character varying` | `NO` |
| `code` | `character varying` | `NO` |
| `name` | `character varying` | `NO` |

### Table: `subscriptions`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `provider` | `character varying` | `NO` |
| `provider_customer_id` | `character varying` | `NO` |
| `provider_subscription_id` | `character varying` | `NO` |
| `status` | `character varying` | `NO` |
| `quantity` | `integer` | `NO` |
| `trial_ends_at` | `timestamp without time zone` | `YES` |
| `ends_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `tags`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `type` | `character varying` | `NO` |

### Table: `task_comments`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `task_id` | `bigint` | `NO` |
| `author_user_id` | `bigint` | `NO` |
| `body` | `text` | `NO` |
| `files` | `jsonb` | `YES` |
| `tags` | `jsonb` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `original_body` | `text` | `YES` |
| `parent_comment_id` | `bigint` | `YES` |

### Table: `task_recurrences`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `created_by_user_id` | `bigint` | `YES` |
| `frequency` | `character varying` | `NO` |
| `weekdays` | `jsonb` | `YES` |
| `day_of_month` | `smallint` | `YES` |
| `start_date` | `date` | `NO` |
| `end_date` | `date` | `YES` |
| `occurrences_count` | `integer` | `YES` |
| `base_title` | `character varying` | `NO` |
| `base_description` | `text` | `YES` |
| `project_id` | `bigint` | `YES` |
| `estimated_hours` | `numeric` | `YES` |
| `default_operators` | `jsonb` | `YES` |
| `is_active` | `boolean` | `NO` |
| `tasks_generated` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `priority` | `character varying` | `YES` |
| `source` | `character varying` | `YES` |
| `country_code` | `character varying` | `YES` |
| `specialty_ids` | `jsonb` | `YES` |

### Table: `task_schedule_person`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `YES` |
| `task_schedule_id` | `bigint` | `YES` |
| `person_id` | `bigint` | `YES` |
| `is_responsible` | `boolean` | `YES` |
| `shift_minutes` | `integer` | `YES` |
| `worked_minutes` | `integer` | `YES` |
| `imputed_minutes` | `integer` | `YES` |
| `started_at` | `timestamp without time zone` | `YES` |
| `finished_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `task_schedule_resource`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `task_schedule_id` | `bigint` | `NO` |
| `resource_id` | `bigint` | `NO` |
| `is_responsible` | `boolean` | `NO` |
| `shift_minutes` | `integer` | `NO` |
| `worked_minutes` | `integer` | `NO` |
| `imputed_minutes` | `integer` | `NO` |
| `started_at` | `timestamp without time zone` | `YES` |
| `finished_at` | `timestamp without time zone` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `order_index` | `integer` | `YES` |

### Table: `task_schedules`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `task_id` | `bigint` | `NO` |
| `scheduled_date` | `date` | `YES` |
| `order` | `integer` | `YES` |
| `type` | `character varying` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `task_templates`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `created_by_user_id` | `bigint` | `YES` |
| `person_id` | `bigint` | `YES` |
| `name` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `estimated_hours` | `numeric` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `leader_person_id` | `bigint` | `YES` |
| `priority` | `character varying` | `NO` |
| `source` | `character varying` | `NO` |
| `shift_hours` | `numeric` | `YES` |
| `hourly_rate` | `numeric` | `YES` |
| `address` | `text` | `YES` |
| `country_code` | `character varying` | `YES` |
| `state` | `character varying` | `YES` |
| `city` | `character varying` | `YES` |
| `postal_code` | `character varying` | `YES` |
| `post_complete_enabled` | `boolean` | `NO` |
| `post_complete_action` | `character varying` | `YES` |
| `post_complete_message` | `text` | `YES` |
| `post_cancel_enabled` | `boolean` | `NO` |
| `post_cancel_action` | `character varying` | `YES` |
| `post_cancel_message` | `text` | `YES` |
| `default_operators` | `jsonb` | `YES` |
| `template_type` | `character varying` | `NO` |
| `frequency` | `character varying` | `YES` |
| `weekdays` | `jsonb` | `YES` |
| `day_of_month` | `smallint` | `YES` |
| `end_mode` | `character varying` | `YES` |
| `occurrences_count` | `smallint` | `YES` |
| `working_days` | `jsonb` | `YES` |

### Table: `tasks`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `project_id` | `bigint` | `YES` |
| `created_by_user_id` | `bigint` | `YES` |
| `person_id` | `bigint` | `YES` |
| `leader_person_id` | `bigint` | `YES` |
| `task_recurrence_id` | `bigint` | `YES` |
| `code` | `character varying` | `YES` |
| `title` | `character varying` | `NO` |
| `description` | `text` | `YES` |
| `address` | `character varying` | `YES` |
| `country_code` | `character varying` | `YES` |
| `state` | `character varying` | `YES` |
| `city` | `character varying` | `YES` |
| `postal_code` | `character varying` | `YES` |
| `status` | `character varying` | `NO` |
| `order` | `integer` | `YES` |
| `priority` | `character varying` | `NO` |
| `started_at` | `timestamp without time zone` | `YES` |
| `completed_at` | `timestamp without time zone` | `YES` |
| `time_to_complete` | `numeric` | `YES` |
| `estimated_hours` | `numeric` | `YES` |
| `shift_hours` | `numeric` | `YES` |
| `hourly_rate` | `numeric` | `YES` |
| `actual_cost` | `numeric` | `NO` |
| `default_operators` | `jsonb` | `YES` |
| `working_days` | `jsonb` | `YES` |
| `source` | `character varying` | `NO` |
| `source_name` | `character varying` | `YES` |
| `source_phone` | `character varying` | `YES` |
| `source_email` | `character varying` | `YES` |
| `post_complete_enabled` | `boolean` | `NO` |
| `post_complete_action` | `character varying` | `YES` |
| `post_complete_message` | `text` | `YES` |
| `post_cancel_enabled` | `boolean` | `NO` |
| `post_cancel_action` | `character varying` | `YES` |
| `post_cancel_message` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `recurrence_scheduled_date` | `date` | `YES` |

### Table: `team_absences`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `start_date` | `date` | `NO` |
| `end_date` | `date` | `NO` |
| `reason` | `character varying` | `NO` |
| `comments` | `text` | `YES` |
| `created_by_user_id` | `bigint` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `team_invitations`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `email` | `character varying` | `YES` |
| `role` | `character varying` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `phone` | `character varying` | `YES` |

### Table: `team_user`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `role` | `character varying` | `YES` |
| `hourly_rate` | `numeric` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `team_workday_settings`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `timezone` | `text` | `NO` |
| `workdays` | `ARRAY` | `NO` |
| `workday_start_time` | `time without time zone` | `NO` |
| `workday_end_time` | `time without time zone` | `NO` |
| `start_reminder_enabled` | `boolean` | `NO` |
| `end_reminder_enabled` | `boolean` | `NO` |
| `start_reminder_offset_minutes` | `integer` | `NO` |
| `end_reminder_offset_minutes` | `integer` | `NO` |
| `start_reminder_cutoff_time` | `time without time zone` | `YES` |
| `end_reminder_cutoff_time` | `time without time zone` | `YES` |
| `is_active` | `boolean` | `NO` |
| `created_at` | `timestamp with time zone` | `NO` |
| `updated_at` | `timestamp with time zone` | `NO` |
| `end_reminder_trigger_mode` | `text` | `NO` |
| `end_reminder_after_start_minutes` | `integer` | `NO` |
| `workday_reminder_recipient_roles` | `ARRAY` | `NO` |

### Table: `teams`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `user_id` | `bigint` | `YES` |
| `name` | `character varying` | `NO` |
| `personal_team` | `boolean` | `NO` |
| `legal_name` | `character varying` | `YES` |
| `vat` | `character varying` | `YES` |
| `domain` | `character varying` | `YES` |
| `status` | `character varying` | `NO` |
| `plan_id` | `bigint` | `YES` |
| `billing_email` | `character varying` | `YES` |
| `billing_name` | `character varying` | `YES` |
| `billing_address` | `text` | `YES` |
| `billing_country` | `character varying` | `YES` |
| `billing_state` | `character varying` | `YES` |
| `billing_city` | `character varying` | `YES` |
| `billing_postal_code` | `character varying` | `YES` |
| `currency` | `character varying` | `YES` |
| `timezone` | `character varying` | `YES` |
| `contact_name` | `character varying` | `YES` |
| `contact_email` | `character varying` | `YES` |
| `contact_phone` | `character varying` | `YES` |
| `workday_start` | `time without time zone` | `YES` |
| `workday_end` | `time without time zone` | `YES` |
| `week_starts_on` | `integer` | `YES` |
| `daily_summary_time` | `time without time zone` | `YES` |
| `working_days` | `jsonb` | `YES` |
| `require_task_approval` | `boolean` | `NO` |
| `allow_auto_schedule` | `boolean` | `NO` |
| `logo_url` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `daily_flow_projects_enabled` | `boolean` | `NO` |
| `company_id` | `bigint` | `YES` |
| `report_language` | `character varying` | `NO` |
| `end_workday_agent_enabled` | `boolean` | `NO` |
| `end_workday_agent_roles` | `ARRAY` | `NO` |

### Table: `time_clock_corrections`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `record_id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `previous_entry_at` | `timestamp without time zone` | `YES` |
| `previous_exit_at` | `timestamp without time zone` | `YES` |
| `new_entry_at` | `timestamp without time zone` | `YES` |
| `new_exit_at` | `timestamp without time zone` | `YES` |
| `reason` | `text` | `NO` |
| `corrected_by_user_id` | `bigint` | `NO` |
| `corrected_at` | `timestamp without time zone` | `NO` |
| `correction_source` | `character varying` | `NO` |

### Table: `time_clock_records`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `work_date` | `date` | `NO` |
| `entry_at` | `timestamp without time zone` | `YES` |
| `exit_at` | `timestamp without time zone` | `YES` |
| `entry_recorded_by_user_id` | `bigint` | `YES` |
| `exit_recorded_by_user_id` | `bigint` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `original_entry_at` | `timestamp without time zone` | `YES` |
| `original_exit_at` | `timestamp without time zone` | `YES` |
| `is_corrected` | `boolean` | `NO` |

### Table: `tools`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `serial_number` | `character varying` | `YES` |
| `brand` | `character varying` | `YES` |
| `model` | `character varying` | `YES` |

### Table: `user_notification_preferences`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `NO` |
| `notification_type_code` | `character varying` | `NO` |
| `channel_code` | `character varying` | `NO` |
| `enabled` | `boolean` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `reminder_days_before` | `integer` | `YES` |

### Table: `users`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `name` | `character varying` | `NO` |
| `email` | `character varying` | `NO` |
| `email_verified_at` | `timestamp without time zone` | `YES` |
| `phone` | `character varying` | `YES` |
| `password` | `character varying` | `NO` |
| `remember_token` | `character varying` | `YES` |
| `current_team_id` | `bigint` | `YES` |
| `profile_photo_path` | `character varying` | `YES` |
| `timezone` | `character varying` | `YES` |
| `language` | `character varying` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `deleted_at` | `timestamp without time zone` | `YES` |
| `two_factor_secret` | `text` | `YES` |
| `two_factor_recovery_codes` | `text` | `YES` |
| `two_factor_confirmed_at` | `timestamp without time zone` | `YES` |
| `is_admin` | `boolean` | `NO` |

### Table: `vehicle_accessories`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `vehicle_id` | `bigint` | `NO` |
| `accessory_id` | `bigint` | `NO` |
| `quantity` | `integer` | `NO` |
| `notes` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `vehicles`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `license_plate` | `character varying` | `NO` |
| `brand` | `character varying` | `YES` |
| `model` | `character varying` | `YES` |
| `daily_rate` | `numeric` | `YES` |

### Table: `voice_inputs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `uuid` | `NO` |
| `log_id` | `bigint` | `NO` |
| `inbound_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `YES` |
| `session_id` | `bigint` | `YES` |
| `task_id` | `bigint` | `YES` |
| `phone` | `text` | `YES` |
| `wa_media_id` | `text` | `YES` |
| `media_mime` | `text` | `YES` |
| `media_duration_ms` | `integer` | `YES` |
| `s3_bucket` | `text` | `YES` |
| `s3_key_original` | `text` | `YES` |
| `s3_key_normalized` | `text` | `YES` |
| `transcript_text` | `text` | `YES` |
| `transcript_lang` | `text` | `YES` |
| `transcript_status` | `text` | `YES` |
| `transcript_ts` | `timestamp without time zone` | `YES` |
| `last_error` | `text` | `YES` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |
| `team_id` | `bigint` | `YES` |
| `dispatched_at` | `timestamp with time zone` | `YES` |

### Table: `whatsapp_action_log`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `process_name` | `text` | `NO` |
| `action_type` | `text` | `NO` |
| `direction` | `text` | `YES` |
| `user_id` | `bigint` | `YES` |
| `session_id` | `bigint` | `YES` |
| `task_id` | `bigint` | `YES` |
| `phone` | `text` | `YES` |
| `wa_message_id` | `text` | `YES` |
| `message_type` | `text` | `YES` |
| `button_id` | `text` | `YES` |
| `message_text` | `text` | `YES` |
| `payload` | `json` | `YES` |
| `created_at` | `timestamp without time zone` | `NO` |

### Table: `whatsapp_bots`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `provider` | `character varying` | `NO` |
| `phone_number_id` | `character varying` | `NO` |
| `webhook_secret` | `character varying` | `NO` |
| `status` | `character varying` | `NO` |
| `config_json` | `jsonb` | `NO` |
| `created_at` | `timestamp without time zone` | `YES` |
| `updated_at` | `timestamp without time zone` | `YES` |

### Table: `whatsapp_comment_links`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `comment_type` | `text` | `NO` |
| `comment_id` | `bigint` | `NO` |
| `inbound_id` | `bigint` | `YES` |
| `wa_message_id` | `text` | `NO` |
| `phone` | `text` | `NO` |
| `user_id` | `bigint` | `YES` |
| `team_id` | `bigint` | `YES` |
| `session_id` | `bigint` | `YES` |
| `created_at` | `timestamp with time zone` | `NO` |
| `updated_at` | `timestamp with time zone` | `NO` |

### Table: `whatsapp_inbound_messages`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `wa_message_id` | `text` | `NO` |
| `phone` | `text` | `YES` |
| `message_type` | `text` | `YES` |
| `wa_media_id` | `text` | `YES` |
| `status` | `text` | `NO` |
| `attempts` | `integer` | `NO` |
| `first_seen_at` | `timestamp with time zone` | `NO` |
| `last_seen_at` | `timestamp with time zone` | `NO` |
| `last_error` | `text` | `YES` |
| `last_log_id` | `bigint` | `YES` |

### Table: `whatsapp_media_inputs`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `uuid` | `NO` |
| `inbound_id` | `bigint` | `NO` |
| `log_id` | `bigint` | `YES` |
| `user_id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `session_id` | `bigint` | `YES` |
| `task_id` | `bigint` | `YES` |
| `phone` | `text` | `NO` |
| `wa_media_id` | `text` | `NO` |
| `media_kind` | `text` | `NO` |
| `media_mime` | `text` | `YES` |
| `caption` | `text` | `YES` |
| `filename` | `text` | `YES` |
| `s3_bucket` | `text` | `YES` |
| `s3_key_original` | `text` | `YES` |
| `file_size` | `bigint` | `YES` |
| `task_comment_id` | `bigint` | `YES` |
| `status` | `text` | `NO` |
| `last_error` | `text` | `YES` |
| `created_at` | `timestamp with time zone` | `NO` |
| `updated_at` | `timestamp with time zone` | `NO` |
| `project_id` | `bigint` | `YES` |
| `project_comment_id` | `bigint` | `YES` |

### Table: `workday_reminder_log`
| Column | Data Type | Nullable |
| --- | --- | --- |
| `id` | `bigint` | `NO` |
| `team_id` | `bigint` | `NO` |
| `person_id` | `bigint` | `NO` |
| `user_id` | `bigint` | `YES` |
| `reminder_type` | `text` | `NO` |
| `reminder_date` | `date` | `NO` |
| `status` | `text` | `NO` |
| `result_reason` | `text` | `YES` |
| `phone` | `text` | `YES` |
| `daily_session_id` | `bigint` | `YES` |
| `template_name` | `text` | `YES` |
| `locked_by` | `text` | `YES` |
| `locked_at` | `timestamp with time zone` | `YES` |
| `attempt_count` | `integer` | `NO` |
| `last_attempt_at` | `timestamp with time zone` | `YES` |
| `sent_at` | `timestamp with time zone` | `YES` |
| `failed_at` | `timestamp with time zone` | `YES` |
| `error_message` | `text` | `YES` |
| `created_at` | `timestamp with time zone` | `NO` |
| `updated_at` | `timestamp with time zone` | `NO` |

