# Google Cloud Model Armor Semantic Firewall & Prompt Shield (<50ms)

resource "google_model_armor_template" "agent_safety_template" {
  provider    = google-beta
  project     = var.project_id
  location    = "global"
  template_id = "altostrat-hr-agent-safety-${var.environment}"

  filter_config {
    rai_settings {
      hate_speech_filter_settings {
        filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
        confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
      }
      harassment_filter_settings {
        filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
        confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
      }
      sexual_filter_settings {
        filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
        confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
      }
      dangerous_filter_settings {
        filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
        confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
      }
    }
    pii_settings {
      dlp_info_types = ["SINGAPORE_NATIONAL_REGISTRATION_ID_NUMBER", "PHONE_NUMBER", "EMAIL_ADDRESS", "STREET_ADDRESS"]
    }
    prompt_injection_settings {
      filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
      confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
    }
    system_override_settings {
      filter_enforcement = "FILTER_ENFORCEMENT_ENABLED"
      confidence_level   = "CONFIDENCE_LEVEL_LOW_AND_ABOVE"
    }
  }

  depends_on = [google_project_service.gemini_enterprise_apis]
}
