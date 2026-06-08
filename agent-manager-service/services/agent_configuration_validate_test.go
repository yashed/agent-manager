package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
	"gorm.io/gorm"

	"github.com/wso2/agent-manager/agent-manager-service/models"
	"github.com/wso2/agent-manager/agent-manager-service/repositories"
	"github.com/wso2/agent-manager/agent-manager-service/utils"
)

// fakeLLMProviderRepo implements LLMProviderRepository for unit tests; only GetByHandle is used.
type fakeLLMProviderRepo struct {
	repositories.LLMProviderRepository
	byHandle map[string]*models.LLMProvider
}

func (f *fakeLLMProviderRepo) GetByHandle(handle, _ string) (*models.LLMProvider, error) {
	if p, ok := f.byHandle[handle]; ok {
		return p, nil
	}
	return nil, gorm.ErrRecordNotFound
}

func TestValidateProvidersInCatalog(t *testing.T) {
	s := &agentConfigurationService{
		llmProviderRepo: &fakeLLMProviderRepo{byHandle: map[string]*models.LLMProvider{
			"good":   {InCatalog: true},
			"notcat": {InCatalog: false},
		}},
	}
	ctx := context.Background()

	require.NoError(t, s.ValidateProvidersInCatalog(ctx, "org", []string{"good", "good"}),
		"valid handle (deduped) passes")
	require.ErrorIs(t, s.ValidateProvidersInCatalog(ctx, "org", []string{"missing"}),
		utils.ErrLLMProviderNotFound)
	require.ErrorIs(t, s.ValidateProvidersInCatalog(ctx, "org", []string{"notcat"}),
		utils.ErrInvalidInput)
	require.ErrorIs(t, s.ValidateProvidersInCatalog(ctx, "org", []string{""}),
		utils.ErrInvalidInput)
}
