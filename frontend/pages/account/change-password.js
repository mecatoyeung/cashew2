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

import AccountLayout from '../../layouts/account'

import service from '../../service'

import accountStyles from '../../styles/Account.module.css'

import Loader from '../../assets/icons/loader.svg'

export default function ResetPassword() {
  const router = useRouter()

  const {} = router.query

  const [changePasswordForm, setChangePasswordForm] = useState({
    oldPassword: '',
    newPassword1: '',
    newPassword2: '',
    submitting: false,
  })

  const [formSuccessMessage, setFormSuccessMessage] = useState('')
  const [formErrorMessage, setFormErrorMessage] = useState(null)

  const oldPasswordChangeHandler = (e) => {
    setChangePasswordForm(
      produce((draft) => {
        draft.oldPassword = e.target.value
      })
    )
  }

  const password1ChangeHandler = (e) => {
    setChangePasswordForm(
      produce((draft) => {
        draft.newPassword1 = e.target.value
      })
    )
  }

  const password2ChangeHandler = (e) => {
    setChangePasswordForm(
      produce((draft) => {
        draft.newPassword2 = e.target.value
      })
    )
  }

  const changePasswordBtnClickHandler = (e) => {
    setFormSuccessMessage('')
    setFormErrorMessage('')
    setChangePasswordForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.post(
      'rest-auth/password/change/',
      {
        ...changePasswordForm,
      },
      (resposne) => {
        setFormSuccessMessage('Password changed successfully!')
        setChangePasswordForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
      },
      (errorResponse) => {
        setFormErrorMessage(
          Object.values(errorResponse.response.data).join('\n')
        )
        setChangePasswordForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
      }
    )
  }

  useEffect(() => {}, [router.isReady])

  return (
    <AccountLayout>
      <h1 className={accountStyles.h1}>Change Password</h1>
      <div className={accountStyles.profileDiv}>
        <Form>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formOldPassword"
            >
              <Form.Label>Old Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                placeholder="Enter old password"
                onChange={(e) => oldPasswordChangeHandler(e)}
                value={changePasswordForm.oldPassword}
              />
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formPassword1"
            >
              <Form.Label>New Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                placeholder="Enter password"
                onChange={(e) => password1ChangeHandler(e)}
                value={changePasswordForm.newPassword1}
              />
            </Form.Group>
          </Row>
          <Row>
            <Form.Group
              as={Col}
              className={accountStyles.col + ' xs-12' + ' md-3'}
              controlId="formPassword2"
            >
              <Form.Label>Confirm New Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                placeholder="Confirm password"
                onChange={(e) => password2ChangeHandler(e)}
                value={changePasswordForm.newPassword2}
              />
            </Form.Group>
          </Row>
          {formSuccessMessage && formSuccessMessage.length > 0 && (
            <Row>
              <div className="formSuccessMessage">{formSuccessMessage}</div>
            </Row>
          )}
          {formErrorMessage && formErrorMessage.length > 0 && (
            <Row>
              <div className="formErrorMessage">{formErrorMessage}</div>
            </Row>
          )}
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
              <Button
                className={
                  accountStyles.changePasswordBtn + ' ' + accountStyles.btn
                }
                onClick={(e) => changePasswordBtnClickHandler(e)}
                disabled={changePasswordForm.submitting}
              >
                {changePasswordForm.submitting && (
                  <img className="spinner" src={Loader.src} />
                )}
                {changePasswordForm.submitting ? 'Loading' : 'Change Password'}
              </Button>
            </Form.Group>
          </Row>
        </Form>
      </div>
    </AccountLayout>
  )
}
