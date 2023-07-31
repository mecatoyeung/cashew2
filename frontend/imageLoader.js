export default function imageLoader({ src }) {
    return `${process.env.NEXT_PUBLIC_DOMAIN}${src}`;
}