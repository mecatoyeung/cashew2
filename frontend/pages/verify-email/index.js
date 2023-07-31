import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'
import Head from 'next/head'

import { produce } from "immer"

import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Form from 'react-bootstrap/Form'
import { Button } from 'react-bootstrap'

import Select from 'react-select'

import service from '../../service'

import OnePageLayout from '../../layouts/onePage'

import verifyEmailStyles from "../../styles/VerifyEmail.module.css"

export default function VerifyEmail() {

  const router = useRouter()

  const { email } = router.query

  useEffect(() => {
  }, [])

  return (
    <>
      <Head>
        <title>Cashew - Verify Email</title>
      </Head>
      <OnePageLayout>
        <div className={verifyEmailStyles.wrapper}>
          <div>
            <h1 className={verifyEmailStyles.h1}>Activate your Email!</h1>
          </div>
          <div className={verifyEmailStyles.form}>
            <Form>
              <Row>
                <Form.Group as={Col} className={verifyEmailStyles.col + " xs-12" + " md-3"}>
                  <Form.Label>We need your help on verifying the following email address: { email }</Form.Label>
                </Form.Group>
              </Row>
              <Row>
                <Form.Group as={Col} className={verifyEmailStyles.actions + " " + verifyEmailStyles.col + " xs-12" + " md-3"}>
                  <Button type="button" className={verifyEmailStyles.signInBtn + " " + verifyEmailStyles.btn} onClick={() => router.push("/signin")}>Sign In After Activation</Button>
                  <Button type="button" className={verifyEmailStyles.homeBtn + " " + verifyEmailStyles.btn + " btn-secondary"} onClick={() => router.push("/")}>Home</Button>
                </Form.Group>
              </Row>
            </Form>
          </div>
        </div>
      </OnePageLayout>
    </>
  )
}
