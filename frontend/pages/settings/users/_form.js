import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Row, Col } from 'react-bootstrap'

import Select from 'react-select'

import Loader from '../../../assets/icons/loader.svg'

import SettingsLayout from '../../../layouts/settings'

import service from '../../../service'

import accountStyles from '../../../styles/Account.module.css'

export default function _UserForm(props) {
  const router = useRouter()

  const { userId } = router.query

  const [userCountries, setUserCountries] = useState([])

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

  const [userForm, setUserForm] = useState({
    id: 0,
    email: '',
    username: '',
    password1: '',
    password2: '',
    profile: {
      fullName: '',
      country: '',
      companyName: '',
    },
    permissions: [],
    submitting: false,
  })

  const [showDeleteUserModal, setShowDeleteUserModal] = useState(false)

  const getUserCountries = () => {
    service.get('/user_countries/', (response) => {
      setUserCountries(response.data)
    })
  }

  const getUser = () => {
    if (!userId) return
    if (userCountries.length == 0) return
    service.get(`/users/${userId}/`, (response) => {
      setUserForm(
        produce((draft) => {
          draft.id = response.data.id
          draft.email = response.data.email
          draft.username = response.data.username
          draft.isActive = response.data.isActive
          draft.profile.fullName = response.data.profile.fullName
          draft.profile.companyName = response.data.profile.companyName
          draft.profile.country = userCountries.find(
            (c) => c.value == response.data.profile.country
          )
          draft.permissions = response.data.permissionCodenames
        })
      )
    })
  }
  const fullNameChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.profile.fullName = e.target.value
      })
    )
  }

  const companyNameChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.profile.companyName = e.target.value
      })
    )
  }

  const countryChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.profile.country = e
      })
    )
  }

  const emailChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.email = e.target.value
        draft.username = e.target.value
      })
    )
  }

  const usernameChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.email = e.target.value
        draft.username = e.target.value
      })
    )
  }

  const password1ChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.password1 = e.target.value
      })
    )
  }

  const password2ChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.password2 = e.target.value
      })
    )
  }

  const isActiveChkChangeHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.isActive = e.target.checked
      })
    )
  }

  const resetPasswordBtnClickHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.post(
      '/rest-auth/password/reset/',
      {
        email: userForm.email,
      },
      (response) => {
        setUserForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        setFormSuccessMessage('Reset password email sent.')
      }
    )
  }

  const addBtnClickHandler = (e) => {
    setFormErrorMessages(null)
    setUserForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.post(
      'rest-auth/registration/',
      {
        isSuperuser: false,
        username: userForm.username,
        email: userForm.email,
        password1: userForm.password1,
        password2: userForm.password2,
        fullName: userForm.profile.fullName,
        country: userForm.profile.country.value,
        companyName: userForm.profile.companyName,
      },
      (response) => {
        if (response.status == 201) {
          setFormSuccessMessage('The account has been created. Please sign in.')
        }
      },
      (error) => {
        console.error(error)
        setUserForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        setFormErrorMessages(error.response.data)
      }
    )
    service.post(
      `/users/`,
      {
        isActive: userForm.isActive,
        profile: {
          fullName: userForm.profile.fullName,
          country: userForm.profile.country.value,
          companyName: userForm.profile.companyName,
          email: userForm.email,
          username: userForm.username,
        },
      },
      (response) => {
        setUserForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        router.push('/settings/users')
      }
    )
  }

  const permissionCheckHandler = (e, permission) => {
    let checked = e.target.checked
    if (checked) {
      setUserForm(
        produce((draft) => {
          if (!draft.permissions.includes(permission))
            draft.permissions.push(permission)
        })
      )
    } else {
      setUserForm(
        produce((draft) => {
          draft.permissions = draft.permissions.filter(
            (item) => item != permission
          )
        })
      )
    }
  }

  const saveBtnClickHandler = (e) => {
    setUserForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.put(
      `/users/${userForm.id}/`,
      {
        isActive: userForm.isActive,
        profile: {
          fullName: userForm.profile.fullName,
          country: userForm.profile.country.value,
          companyName: userForm.profile.companyName,
        },
        permissionCodenames: userForm.permissions,
      },
      (response) => {
        setUserForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
        router.push('/settings/users')
      }
    )
  }

  const deleteUserBtnClickHandler = () => {
    setShowDeleteUserModal(true)
  }

  const closeDeleteUserModalHandler = () => {
    setShowDeleteUserModal(false)
  }

  const confirmDeleteUserBtnClickHandler = () => {
    service.delete(`/users/${userForm.id}/`, (response) => {
      setUserForm(
        produce((draft) => {
          draft.submitting = false
        })
      )
      router.push('/settings/users')
    })
  }

  const backBtnClickHandler = () => {
    router.push('/settings/users/')
  }

  useEffect(() => {
    getUserCountries()
  }, [])

  useEffect(() => {
    getUser()
  }, [userId, userCountries])

  return (
    <SettingsLayout>
      <h1 className={accountStyles.h1}>
        {props.type == 'add' && <>Add User</>}
        {props.type == 'edit' && <>Edit User</>}
      </h1>
      <div className={accountStyles.profileDiv}>
        <Form>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formFullName"
            >
              <Form.Label>Full Name</Form.Label>
              <Form.Control
                type="text"
                name="fullName"
                placeholder="Enter full name"
                onChange={(e) => fullNameChangeHandler(e)}
                value={userForm.profile.fullName}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.fullName}
                </div>
              )}
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formCountry"
            >
              <Form.Label>Country</Form.Label>
              <Select
                instanceId="userCountriesSelectId"
                options={userCountries}
                onChange={countryChangeHandler}
                value={userForm.profile.country}
              />
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formCompanyName"
            >
              <Form.Label>Company Name</Form.Label>
              <Form.Control
                type="text"
                name="companyName"
                placeholder="Enter company name"
                onChange={(e) => companyNameChangeHandler(e)}
                value={userForm.profile.companyName}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.companyName}
                </div>
              )}
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formEmail"
            >
              <Form.Label>Email</Form.Label>
              <Form.Control
                type="email"
                name="email"
                placeholder="Enter email"
                autoComplete="email"
                disabled={props.type == 'edit'}
                onChange={emailChangeHandler}
                value={userForm.email}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.email}
                </div>
              )}
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formUsername"
            >
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                name="username"
                placeholder="Enter username"
                autoComplete="username"
                disabled={props.type == 'edit'}
                onChange={usernameChangeHandler}
                value={userForm.username}
              />
              {!formValidation.isValid && (
                <div className="formErrorMessage">
                  {formValidation.errorMessages.username}
                </div>
              )}
            </Form.Group>
          </Row>
          {props.type == 'add' && (
            <>
              <Row>
                <Form.Group
                  as={Col}
                  className={accountStyles.col + ' xs-12' + ' md-3'}
                  controlId="formPassword1"
                >
                  <Form.Label>Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    placeholder="Enter Password"
                    autoComplete="password"
                    onChange={password1ChangeHandler}
                    value={userForm.password1}
                  />
                  {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.password1}
                    </div>
                  )}
                </Form.Group>
              </Row>
              <Row>
                <Form.Group
                  as={Col}
                  className={accountStyles.col + ' xs-12' + ' md-3'}
                  controlId="formPassword2"
                >
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    name="password"
                    placeholder="Confirm Password"
                    autoComplete="password"
                    onChange={password2ChangeHandler}
                    value={userForm.password2}
                  />
                  {!formValidation.isValid && (
                    <div className="formErrorMessage">
                      {formValidation.errorMessages.password1}
                    </div>
                  )}
                </Form.Group>
              </Row>
            </>
          )}
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formIsActive"
            >
              <Form.Check
                type="checkbox"
                label={'Is Active'}
                id={`is-active`}
                checked={userForm.isActive}
                onChange={isActiveChkChangeHandler}
              />
            </Form.Group>
          </Row>
          <Row>
            {props.type == 'edit' && (
              <Form.Group
                as={Col}
                className={accountStyles.col + ' xs-12' + ' md-12'}
                controlId="formPermissions"
              >
                <Form.Label>Permissions</Form.Label>
                <Form.Check
                  label="User Management"
                  onChange={(e) =>
                    permissionCheckHandler(e, 'cashew_user_management')
                  }
                  checked={userForm.permissions.includes(
                    'cashew_user_management'
                  )}
                />
                <Form.Check
                  label="Parser Management"
                  onChange={(e) =>
                    permissionCheckHandler(e, 'cashew_parser_management')
                  }
                  checked={userForm.permissions.includes(
                    'cashew_parser_management'
                  )}
                />
                <Form.Check
                  label="User can assign another user to the parser"
                  onChange={(e) =>
                    permissionCheckHandler(
                      e,
                      'cashew_parser_assign_permissions'
                    )
                  }
                  checked={userForm.permissions.includes(
                    'cashew_parser_assign_permissions'
                  )}
                />
                {!formValidation.isValid && (
                  <div className="formErrorMessage">
                    {formValidation.errorMessages.permissionCodenames}
                  </div>
                )}
              </Form.Group>
            )}
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
                  disabled={userForm.submitting}
                >
                  {userForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {userForm.submitting ? 'Loading' : 'Create'}
                </Button>
              )}
              {props.type == 'edit' && (
                <Button
                  className={accountStyles.saveBtn + ' ' + accountStyles.btn}
                  style={{ marginRight: 10 }}
                  onClick={(e) => saveBtnClickHandler(e)}
                  disabled={userForm.submitting}
                >
                  {userForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {userForm.submitting ? 'Loading' : 'Save'}
                </Button>
              )}
              {props.type == 'edit' && (
                <Button
                  className={
                    accountStyles.resetPasswordBtn + ' ' + accountStyles.btn
                  }
                  style={{ marginRight: 10 }}
                  onClick={(e) => resetPasswordBtnClickHandler(e)}
                  disabled={userForm.submitting}
                >
                  {userForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {userForm.submitting ? 'Loading' : 'Reset Password'}
                </Button>
              )}
              {props.type == 'edit' && (
                <Button
                  className={accountStyles.deleteBtn + ' ' + accountStyles.btn}
                  variant="danger"
                  style={{ marginRight: 10 }}
                  onClick={(e) => deleteUserBtnClickHandler(e)}
                  disabled={userForm.submitting}
                >
                  {userForm.submitting && (
                    <img className="spinner" src={Loader.src} />
                  )}
                  {userForm.submitting ? 'Loading' : 'Delete'}
                </Button>
              )}
              <Modal
                show={showDeleteUserModal}
                onHide={closeDeleteUserModalHandler}
              >
                <Modal.Header closeButton>
                  <Modal.Title>Are you sure to delete this user?</Modal.Title>
                </Modal.Header>
                <Modal.Body></Modal.Body>
                <Modal.Footer>
                  <Button
                    variant="danger"
                    onClick={confirmDeleteUserBtnClickHandler}
                  >
                    Yes, I know that all parsers information created by this
                    user will also be deleted.
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={closeDeleteUserModalHandler}
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
