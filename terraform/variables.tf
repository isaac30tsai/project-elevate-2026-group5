variable "project_id" {
  description = "GCP Project ID for Argolis / Altostrat environment"
  type        = string
  default     = "junho-elevate"
}

variable "region" {
  description = "Primary GCP Region for Agent Runtime and Data Stores"
  type        = string
  default     = "asia-southeast1"
}

variable "environment" {
  description = "Deployment environment (dev, uat, prod)"
  type        = string
  default     = "dev"
}

variable "gemini_enterprise_region" {
  description = "Region for Gemini Enterprise front door"
  type        = string
  default     = "global"
}

variable "mcp_auth_token_secret" {
  description = "Secret name for FastMCP backend token in Secret Manager"
  type        = string
  default     = "altostrat-mcp-token"
}
