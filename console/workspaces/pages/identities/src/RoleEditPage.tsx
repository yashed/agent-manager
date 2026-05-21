/**
 * Copyright (c) 2026, WSO2 LLC. (https://www.wso2.com).
 *
 * WSO2 LLC. licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except
 * in compliance with the License. You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

import React, { useMemo, useState } from "react";
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  CircularProgress,
  Divider,
  IconButton,
  ListingTable,
  Stack,
  Tab,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from "@wso2/oxygen-ui";
import { Trash } from "@wso2/oxygen-ui-icons-react";
import { generatePath, useNavigate, useParams } from "react-router-dom";
import {
  useAllUsers,
  useAllGroups,
  useGetRoleAssignments,
  useAddRoleAssignees,
  useRemoveRoleAssignees,
} from "@agent-management-platform/api-client";
import { PageLayout } from "@agent-management-platform/views";
import { absoluteRouteMap, type ThunderUser, type ThunderGroup } from "@agent-management-platform/types";

export const RoleEditPage: React.FC = () => {
  const { orgId, roleId } = useParams<{ orgId: string; roleId: string }>();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState<"users" | "groups">("users");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | undefined>();

  const { data: assignmentsData, isLoading: isLoadingAssignments } = useGetRoleAssignments({
    orgName: orgId,
    roleId: roleId ?? "",
  });
  const { data: allUsersData, isLoading: isLoadingUsers } = useAllUsers({ orgName: orgId });
  const { data: allGroupsData, isLoading: isLoadingGroups } = useAllGroups({ orgName: orgId });

  const { mutateAsync: addAssignees } = useAddRoleAssignees();
  const { mutateAsync: removeAssignees } = useRemoveRoleAssignees();

  const initialUsers: ThunderUser[] = useMemo(
    () => assignmentsData?.users ?? [],
    [assignmentsData],
  );
  const initialGroups: ThunderGroup[] = useMemo(
    () => assignmentsData?.groups ?? [],
    [assignmentsData],
  );
  const allUsers: ThunderUser[] = useMemo(() => allUsersData?.users ?? [], [allUsersData]);
  const allGroups: ThunderGroup[] = useMemo(() => allGroupsData?.groups ?? [], [allGroupsData]);

  // User tab delta tracking
  const [pendingUserAdds, setPendingUserAdds] = useState<ThunderUser[]>([]);
  const [removedUserIds, setRemovedUserIds] = useState<Set<string>>(new Set());

  // Group tab delta tracking
  const [pendingGroupAdds, setPendingGroupAdds] = useState<ThunderGroup[]>([]);
  const [removedGroupIds, setRemovedGroupIds] = useState<Set<string>>(new Set());

  const rolesPath = orgId
    ? generatePath(
        (absoluteRouteMap.children.org.children as unknown as {
          identities: { children: { roles: { path: string } } };
        }).identities.children.roles.path,
        { orgId },
      )
    : "#";

  // Derived displayed lists
  const displayedUsers = useMemo(() => {
    const base = initialUsers.filter((u) => !removedUserIds.has(u.id));
    return [...base, ...pendingUserAdds];
  }, [initialUsers, pendingUserAdds, removedUserIds]);

  const displayedGroups = useMemo(() => {
    const base = initialGroups.filter((g) => !removedGroupIds.has(g.id));
    return [...base, ...pendingGroupAdds];
  }, [initialGroups, pendingGroupAdds, removedGroupIds]);

  const displayedUserIds = useMemo(
    () => new Set(displayedUsers.map((u) => u.id)),
    [displayedUsers],
  );
  const displayedGroupIds = useMemo(
    () => new Set(displayedGroups.map((g) => g.id)),
    [displayedGroups],
  );

  const availableUsers = useMemo(
    () => allUsers.filter((u) => !displayedUserIds.has(u.id)),
    [allUsers, displayedUserIds],
  );
  const availableGroups = useMemo(
    () => allGroups.filter((g) => !displayedGroupIds.has(g.id)),
    [allGroups, displayedGroupIds],
  );

  const getUsername = (user: ThunderUser) =>
    String(user.attributes?.["username"] ?? user.id ?? "");

  const handleAddUser = (_e: React.SyntheticEvent, value: ThunderUser | null) => {
    if (!value) return;
    if (removedUserIds.has(value.id)) {
      setRemovedUserIds((prev) => { const n = new Set(prev); n.delete(value.id); return n; });
    } else {
      setPendingUserAdds((prev) => [...prev, value]);
    }
  };

  const handleRemoveUser = (userId: string) => {
    if (pendingUserAdds.find((u) => u.id === userId)) {
      setPendingUserAdds((prev) => prev.filter((u) => u.id !== userId));
    } else {
      setRemovedUserIds((prev) => new Set([...prev, userId]));
    }
  };

  const handleAddGroup = (_e: React.SyntheticEvent, value: ThunderGroup | null) => {
    if (!value) return;
    if (removedGroupIds.has(value.id)) {
      setRemovedGroupIds((prev) => { const n = new Set(prev); n.delete(value.id); return n; });
    } else {
      setPendingGroupAdds((prev) => [...prev, value]);
    }
  };

  const handleRemoveGroup = (groupId: string) => {
    if (pendingGroupAdds.find((g) => g.id === groupId)) {
      setPendingGroupAdds((prev) => prev.filter((g) => g.id !== groupId));
    } else {
      setRemovedGroupIds((prev) => new Set([...prev, groupId]));
    }
  };

  const handleSave = async () => {
    if (!orgId || !roleId) return;
    setSaveError(undefined);
    setIsSaving(true);
    try {
      const params = { orgName: orgId, roleId };
      const addUserIds = pendingUserAdds.map((u) => u.id);
      const removeUserIds = [...removedUserIds];
      const addGroupIds = pendingGroupAdds.map((g) => g.id);
      const removeGroupIds = [...removedGroupIds];
      if (addUserIds.length > 0) {
        await addAssignees({ params, body: { userIds: addUserIds } });
      }
      if (removeUserIds.length > 0) {
        await removeAssignees({ params, body: { userIds: removeUserIds } });
      }
      if (addGroupIds.length > 0) {
        await addAssignees({ params, body: { groupIds: addGroupIds } });
      }
      if (removeGroupIds.length > 0) {
        await removeAssignees({ params, body: { groupIds: removeGroupIds } });
      }
      navigate(rolesPath);
    } catch {
      setSaveError("Failed to update role assignments. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const isLoading = isLoadingAssignments || isLoadingUsers || isLoadingGroups;

  if (isLoading) {
    return (
      <PageLayout title="Edit Role" disableIcon>
        <Box display="flex" justifyContent="center" mt={4}>
          <CircularProgress />
        </Box>
      </PageLayout>
    );
  }

  return (
    <PageLayout title="Edit Role" backHref={rolesPath} backLabel="Back to Roles" disableIcon>
      <Stack spacing={3} sx={{ maxWidth: 800 }}>
        {saveError != null && <Alert severity="error">{saveError}</Alert>}

        <Tabs
          value={activeTab}
          onChange={(_e, newValue) => setActiveTab(newValue as "users" | "groups")}
        >
          <Tab label="Users" value="users" />
          <Tab label="Groups" value="groups" />
        </Tabs>

        {activeTab === "users" && (
          <Box>
            <Typography variant="subtitle1" fontWeight={600} mb={1}>
              Assigned Users
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Search and add users to this role.
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Autocomplete
              options={availableUsers}
              getOptionLabel={(option) => getUsername(option as ThunderUser)}
              onChange={handleAddUser}
              value={null}
              renderInput={(params) => (
                <TextField {...params} placeholder="Search users..." label="Add User" />
              )}
              noOptionsText="No users available"
              sx={{ mb: 2 }}
            />

            {displayedUsers.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No users assigned yet. Search and add users above.
              </Typography>
            ) : (
              <ListingTable.Container>
                <ListingTable>
                  <ListingTable.Head>
                    <ListingTable.Row>
                      <ListingTable.Cell>Username</ListingTable.Cell>
                      <ListingTable.Cell>User ID</ListingTable.Cell>
                      <ListingTable.Cell />
                    </ListingTable.Row>
                  </ListingTable.Head>
                  <ListingTable.Body>
                    {displayedUsers.map((user) => (
                      <ListingTable.Row key={user.id}>
                        <ListingTable.Cell>{getUsername(user)}</ListingTable.Cell>
                        <ListingTable.Cell>{user.id}</ListingTable.Cell>
                        <ListingTable.Cell align="right">
                          <Tooltip title="Remove from role">
                            <IconButton size="small" onClick={() => handleRemoveUser(user.id)}>
                              <Trash size={16} />
                            </IconButton>
                          </Tooltip>
                        </ListingTable.Cell>
                      </ListingTable.Row>
                    ))}
                  </ListingTable.Body>
                </ListingTable>
              </ListingTable.Container>
            )}
          </Box>
        )}

        {activeTab === "groups" && (
          <Box>
            <Typography variant="subtitle1" fontWeight={600} mb={1}>
              Assigned Groups
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              Search and add groups to this role.
            </Typography>
            <Divider sx={{ mb: 2 }} />

            <Autocomplete
              options={availableGroups}
              getOptionLabel={(option) => (option as ThunderGroup).name}
              onChange={handleAddGroup}
              value={null}
              renderInput={(params) => (
                <TextField {...params} placeholder="Search groups..." label="Add Group" />
              )}
              noOptionsText="No groups available"
              sx={{ mb: 2 }}
            />

            {displayedGroups.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No groups assigned yet. Search and add groups above.
              </Typography>
            ) : (
              <ListingTable.Container>
                <ListingTable>
                  <ListingTable.Head>
                    <ListingTable.Row>
                      <ListingTable.Cell>Name</ListingTable.Cell>
                      <ListingTable.Cell>Description</ListingTable.Cell>
                      <ListingTable.Cell />
                    </ListingTable.Row>
                  </ListingTable.Head>
                  <ListingTable.Body>
                    {displayedGroups.map((group) => (
                      <ListingTable.Row key={group.id}>
                        <ListingTable.Cell>{group.name}</ListingTable.Cell>
                        <ListingTable.Cell>{group.description ?? "-"}</ListingTable.Cell>
                        <ListingTable.Cell align="right">
                          <Tooltip title="Remove from role">
                            <IconButton size="small" onClick={() => handleRemoveGroup(group.id)}>
                              <Trash size={16} />
                            </IconButton>
                          </Tooltip>
                        </ListingTable.Cell>
                      </ListingTable.Row>
                    ))}
                  </ListingTable.Body>
                </ListingTable>
              </ListingTable.Container>
            )}
          </Box>
        )}

        <Stack direction="row" spacing={1} justifyContent="flex-end">
          <Button variant="outlined" onClick={() => navigate(rolesPath)} disabled={isSaving}>
            Cancel
          </Button>
          <Button variant="contained" onClick={handleSave} disabled={isSaving}>
            {isSaving ? "Saving..." : "Save Changes"}
          </Button>
        </Stack>
      </Stack>
    </PageLayout>
  );
};
