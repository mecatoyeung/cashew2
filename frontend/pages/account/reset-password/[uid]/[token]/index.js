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

import AccountLayout from '../../../../../layouts/account'

import service from '../../../../../service'

import accountStyles from '../../../../../styles/Account.module.css'

import Loader from '../../../../../assets/icons/loader.svg'

export default function ResetPassword() {
  const router = useRouter()

  const { uid, token } = router.query

  const [resetPasswordForm, setResetPasswordForm] = useState({
    oldPassword: '',
    newPassword1: '',
    newPassword2: '',
    submitting: false,
  })

  const [formSuccessMessage, setFormSuccessMessage] = useState('')
  const [formErrorMessage, setFormErrorMessage] = useState(null)

  const newPassword1ChangeHandler = (e) => {
    setResetPasswordForm(
      produce((draft) => {
        draft.newPassword1 = e.target.value
      })
    )
  }

  const newPassword2ChangeHandler = (e) => {
    setResetPasswordForm(
      produce((draft) => {
        draft.newPassword2 = e.target.value
      })
    )
  }

  const resetPasswordBtnClickHandler = (e) => {
    setFormSuccessMessage('')
    setFormErrorMessage('')
    setResetPasswordForm(
      produce((draft) => {
        draft.submitting = true
      })
    )
    service.post(
      'rest-auth/password/reset/confirm/',
      {
        ...resetPasswordForm,
        uid: uid,
        token: token,
      },
      (resposne) => {
        setFormSuccessMessage('Password reset successfully!')
        setResetPasswordForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
      },
      (errorResponse) => {
        setFormErrorMessage(
          Object.values(errorResponse.response.data).join('\n')
        )
        setResetPasswordForm(
          produce((draft) => {
            draft.submitting = false
          })
        )
      }
    )
  }

  const backToSignInBtnClickHandler = () => {
    router.push('/signin')
  }

  useEffect(() => {}, [router.isReady])

  return (
    <>
      <h1
        className={accountStyles.h1}
        style={{ display: 'block', textAlign: 'center' }}
      >
        Change Password
      </h1>
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
                name="password1"
                placeholder="Enter new password"
                onChange={(e) => newPassword1ChangeHandler(e)}
                value={resetPasswordForm.newPassword1}
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
                name="password2"
                placeholder="Confirm new password"
                onChange={(e) => newPassword2ChangeHandler(e)}
                value={resetPasswordForm.newPassword2}
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
                style={{ marginRight: 10 }}
                onClick={(e) => resetPasswordBtnClickHandler(e)}
                disabled={resetPasswordForm.submitting}
              >
                {resetPasswordForm.submitting && (
                  <img className="spinner" src={Loader.src} />
                )}
                {resetPasswordForm.submitting ? 'Loading' : 'Reset Password'}
              </Button>
              <Button
                className={
                  accountStyles.changePasswordBtn + ' ' + accountStyles.btn
                }
                variant="secondary"
                onClick={(e) => backToSignInBtnClickHandler(e)}
                disabled={resetPasswordForm.submitting}
              >
                {resetPasswordForm.submitting && (
                  <img className="spinner" src={Loader.src} />
                )}
                {resetPasswordForm.submitting
                  ? 'Loading'
                  : 'Back to Sign In page'}
              </Button>
            </Form.Group>
          </Row>
        </Form>
      </div>
    </>
  )
}
