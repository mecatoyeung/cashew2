import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form, FormCheck } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Row, Col } from 'react-bootstrap'

import Select from 'react-select'

import Loader from '../../../assets/icons/loader.svg'

import SettingsLayout from '../../../layouts/settings'

import service from '../../../service'

import accountStyles from '../../../styles/Account.module.css'

export default function _GroupForm(props) {
  const router = useRouter()

  const { groupId } = router.query

  const [formSuccessMessage, setFormSuccessMessage] = useState('')
  const [formErrorMessages, setFormErrorMessages] = useState(null)

  const [formValidation, setFormValidation] = useState({
    isValid: true,
    errorMessages: {
      fullName: '',
      country: '',
      companyName: '',
    },
  })

  const [users, setUsers] = useState([])

  const [groupForm, setGroupForm] = useState({
    id: 0,
    name: '',
    userSet: [],
    permissions: [],
    submitting: false,
  })

  const [showDeleteGroupModal, setShowDeleteGroupModal] = useState(false)

  const getGroup = () => {
    if (!groupId) return
    if (users.length == 0) return
    service.get(`/groups/${groupId}/`, (response) => {
      console.log(response)
      setGroupForm(
        produce((draft) => {
          draft.id = response.data.id
          draft.name = response.data.name
          draft.userSet = response.data.userSet.map((userId) => {
            return users.find((u) => u.value == userId)
          })
          draft.permissions = response.data.permissionCodenames
        })
      )
    })
  }

  const getUsers = () => {
    service.get(`/users/`, (response) => {
      setUsers(
        response.data.map((user) => {
          return {
            label: user.profile.fullName,
            value: user.id,
          }
        })
      )
    })
  }

  const nameChangeHandler = (e) => {
    setGroupForm(
      produce((draft) => {
        draft.name = e.target.value
      })
    )
  }

  const addBtnClickHandler = (e) => {
    setGroupForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.post(
      `/groups/`,
      {
        name: groupForm.name,
        userSet: groupForm.userSet.map((userId) => userId.value),
        permissionCodenames: groupForm.permissions,
      },
      (response) => {
        setGroupForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        router.push('/settings/groups')
      },
      (error) => {
        setGroupForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        setFormErrorMessages(error.response.data)
      }
    )
  }

  const saveBtnClickHandler = (e) => {
    console.log(groupForm)
    service.put(
      `/groups/${groupForm.id}/`,
      {
        name: groupForm.name,
        userSet: groupForm.userSet.map((userId) => userId.value),
        permissionCodenames: groupForm.permissions,
      },
      (response) => {
        setGroupForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        router.push('/settings/groups')
      }
    )
  }

  const usersInGroupChangeHandler = (e) => {
    setGroupForm(
      produce((draft) => {
        draft.userSet = e
      })
    )
  }

  const permissionCheckHandler = (e, permission) => {
    let checked = e.target.checked
    if (checked) {
      setGroupForm(
        produce((draft) => {
          if (!draft.permissions.includes(permission))
            draft.permissions.push(permission)
        })
      )
    } else {
      setGroupForm(
        produce((draft) => {
          draft.permissions = draft.permissions.filter(
            (item) => item != permission
          )
        })
      )
    }
  }

  const deleteGroupBtnClickHandler = () => {
    setShowDeleteGroupModal(true)
  }

  const closeDeleteGroupModalHandler = () => {
    setShowDeleteGroupModal(false)
  }

  const confirmDeleteGroupBtnClickHandler = () => {
    service.delete(`/groups/${groupForm.id}/`, (response) => {
      setGroupForm(
        produce((draft) => {
          draft.submitting = false
        })
      )
      router.push('/settings/groups')
    })
  }

  const backBtnClickHandler = () => {
    router.push('/settings/groups/')
  }

  useEffect(() => {
    getUsers()
  }, [])

  useEffect(() => {
    getGroup()
  }, [groupId, users])

  return (
    <SettingsLayout>
      <h1 className={accountStyles.h1}>Group</h1>
      <div className={accountStyles.groupsDiv}>
        <Form>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-12'}
              controlId="formName"
            >
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                placeholder="Enter name"
                onChange={(e) => nameChangeHandler(e)}
                value={groupForm.name}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.name}
                </div>
              )}
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-12'}
              controlId="formUsers"
            >
              <Form.Label>Users in the group</Form.Label>
              <Select
                instanceId="users-in-group"
                value={groupForm.userSet}
                isMulti
                name="colors"
                options={users}
                onChange={usersInGroupChangeHandler}
                className="basic-multi-select"
                classNamePrefix="select"
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.userSet}
                </div>
              )}
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-12'}
              controlId="formPermissions"
            >
              <Form.Label>Permissions</Form.Label>
              <FormCheck
                label="User Management"
                onChange={(e) =>
                  permissionCheckHandler(e, 'cashew_user_management')
                }
                checked={groupForm.permissions.includes(
                  'cashew_user_management'
                )}
              />
              <FormCheck
                label="Parser Management"
                onChange={(e) =>
                  permissionCheckHandler(e, 'cashew_parser_management')
                }
                checked={groupForm.permissions.includes(
                  'cashew_parser_management'
                )}
              />
              <FormCheck
                label="User can assign another user to the parser"
                onChange={(e) =>
                  permissionCheckHandler(e, 'cashew_parser_assign_permissions')
                }
                checked={groupForm.permissions.includes(
                  'cashew_parser_assign_permissions'
                )}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.permissionCodenames}
                </div>
              )}
            </Form.Group>
          </Row>
          {formSuccessMessage && formSuccessMessage.length > 0 && (
            <Row>
              <div className="formSuccessMessage">{formSuccessMessage}</div>
            </Row>
          )}
          <Row>
            {formErrorMessages &&
              Object.keys(formErrorMessages).length > 0 &&
              Object.keys(formErrorMessages).map(function (key, index) {
                return formErrorMessages[key].map((message) => {
                  return (
                    <div className="formErrorMessage" key={message}>
                      {message}
                    </div>
                  )
                })
              })}
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={
                accountStyles.actions +
                ' ' +
                accountStyles.col +
                ' xs-12' +
                ' md-3'
              }
            >
              {props.type == 'add' && (
                <Button
                  className={accountStyles.saveBtn + ' ' + accountStyles.btn}
                  style={{ marginRight: 10 }}
                  onClick={(e) => addBtnClickHandler(e)}
                  disabled={groupForm.submitting}
                >
                  {groupForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {groupForm.submitting ? 'Loading' : 'Add'}
                </Button>
              )}
              {props.type == 'edit' && (
                <Button
                  className={accountStyles.saveBtn + ' ' + accountStyles.btn}
                  style={{ marginRight: 10 }}
                  onClick={(e) => saveBtnClickHandler(e)}
                  disabled={groupForm.submitting}
                >
                  {groupForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {groupForm.submitting ? 'Loading' : 'Save'}
                </Button>
              )}
              {props.type == 'edit' && (
                <Button
                  className={accountStyles.deleteBtn + ' ' + accountStyles.btn}
                  variant="danger"
                  style={{ marginRight: 10 }}
                  onClick={(e) => deleteGroupBtnClickHandler(e)}
                  disabled={groupForm.submitting}
                >
                  {groupForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {groupForm.submitting ? 'Loading' : 'Delete'}
                </Button>
              )}
              <Modal
                show={showDeleteGroupModal}
                onHide={closeDeleteGroupModalHandler}
              >
                <Modal.Header closeButton>
                  <Modal.Title>Are you sure to delete this group?</Modal.Title>
                </Modal.Header>
                <Modal.Body></Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="danger"
                    onClick={confirmDeleteGroupBtnClickHandler}
                  >
                    Yes.
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={closeDeleteGroupModalHandler}
                  >
                    Close
                  </Button>
                </Modal.Footer>
              </Modal>
              <Button variant="secondary" onClick={backBtnClickHandler}>
                Back
              </Button>
            </Form.Group>
          </Row>
        </Form>
      </div>
    </SettingsLayout>
  )
}
