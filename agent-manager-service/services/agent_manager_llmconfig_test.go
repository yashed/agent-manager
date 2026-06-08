package services

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"

	"github.com/wso2/agent-manager/agent-manager-service/models"
	"github.com/wso2/agent-manager/agent-manager-service/spec"
)

// spyConfigService records the request passed to Create. Only Create is exercised;
// the embedded interface satisfies the rest (and panics if any other method is called).
type spyConfigService struct {
	AgentConfigurationService
	lastReq models.CreateAgentModelConfigRequest
}

func (s *spyConfigService) Create(_ context.Context, _, _, _ string,
	req models.CreateAgentModelConfigRequest, _ string,
) (*models.AgentModelConfigResponse, error) {
	s.lastReq = req
	return &models.AgentModelConfigResponse{}, nil
}

func TestCreateAgentLLMConfigs_KeysUnderFirstEnv(t *testing.T) {
	spy := &spyConfigService{}
	s := &agentManagerService{agentConfigurationService: spy}

	req := &spec.CreateAgentRequest{
		Name:        "my-agent",
		ModelConfig: []spec.ModelConfigRequest{{ProviderName: "openai"}},
	}

	err := s.createAgentLLMConfigs(context.Background(), "org", "proj", "Development", req)
	require.NoError(t, err)

	require.Len(t, spy.lastReq.EnvMappings, 1, "exactly one env mapping")
	got, ok := spy.lastReq.EnvMappings["Development"]
	require.True(t, ok, "config must be keyed under firstEnv")
	require.Equal(t, "openai", got.ProviderName)
}
