// Copyright (c) 2026, WSO2 LLC. (https://www.wso2.com).
//
// WSO2 LLC. licenses this file to you under the Apache License,
// Version 2.0 (the "License"); you may not use this file except
// in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package spec

// LLMCompletionMessage is a single chat message (role + content).
type LLMCompletionMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// LLMCompletionRequest is the payload for POST .../completions.
type LLMCompletionRequest struct {
	Model    string                 `json:"model,omitempty"`
	Messages []LLMCompletionMessage `json:"messages"`
}

// LLMCompletionResponse is returned after a successful upstream call.
type LLMCompletionResponse struct {
	Content string `json:"content"`
}
