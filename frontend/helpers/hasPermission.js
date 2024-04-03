import CryptoJS from 'crypto-js'

export default function hasPermission(checkingPermission) {
  if (typeof window == 'undefined') {
    return false
  }
  let allPermissions = JSON.parse(
    CryptoJS.AES.decrypt(
      localStorage.getItem('permissions'),
      'sonikgloballimited'
    ).toString(CryptoJS.enc.Utf8)
  )
  console.log(allPermissions)
  return allPermissions.includes(checkingPermission)
}
